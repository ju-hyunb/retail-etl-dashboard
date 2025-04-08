from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, sum, year, month, to_timestamp, when, hour
from download_jdbc_driver import download_mysql_driver
import os
import time
import logging
import datetime
import inspect
import json


def log_info(message: str):
	# define log file
	todayDT = datetime.datetime.now().strftime("%Y%m%d")
	log_dir = "logs"
	os.makedirs(log_dir, exist_ok=True)
	log_file = os.path.join(log_dir, f"{todayDT}_RetailETL.log")

	# create logger
	logger = logging.getLogger("RetailETL")

	if not logger.handlers:
		# define log format
		log_format = "[%(asctime)s][L%(lineno)d] %(message)s"
		log_datefmt = "%Y-%m-%d %H:%M:%S"
		formatter = logging.Formatter(fmt=log_format, datefmt=log_datefmt)

		# set handler (file)
		file_handler = logging.FileHandler(log_file)
		file_handler.setFormatter(formatter)

		# set handler (console)
		stream_handler = logging.StreamHandler()
		stream_handler.setFormatter(formatter)

		logger.setLevel(logging.INFO)
		logger.addHandler(file_handler)
		logger.addHandler(stream_handler)

	# tracking called functions
	frame = inspect.currentframe().f_back
	func_name = frame.f_code.co_name
	lineno = frame.f_lineno

	logger.info(f"[{func_name}][L{lineno}] {message}")


def init_spark(app_name: str = "OnlineRetailETL", useDB=False) -> SparkSession:
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	config_path = os.path.join(BASE_DIR, "config", "spark.json")

	def configure_spark(spark: SparkSession, config_path=config_path):
		with open(config_path, "r") as f:
			configs = json.load(f)
		for key, value in configs.items():
			spark.conf.set(key, value)

	if useDB:
		download_mysql_driver()
		spark = SparkSession.builder \
			.appName(app_name) \
			.master("local[*]") \
			.config("spark.driver.extraClassPath", "jars/mysql-connector-j-8.3.0.jar") \
			.getOrCreate()
	else:
		spark = SparkSession.builder \
			.appName(app_name) \
			.master("local[*]") \
			.getOrCreate()

	spark.sparkContext.setLogLevel("WARN")
	configure_spark(spark)
	return spark


def load_data_from_csv(spark: SparkSession, path: str) -> DataFrame:
	log_info("Loading from csv file ...")
	try:
		return spark.read.csv(path, header=True, inferSchema=True)
	except Exception as e:
		log_info(e)
		return None


def load_data_from_db(spark: SparkSession, config_path="config/db.json") -> DataFrame:
	log_info("Loading from DataBase ...")
	with open(config_path, "r") as f:
		db_config = json.load(f)

	conf = db_config["mysql"]
	jdbc_url = conf["jdbc_url"]
	db_properties = {
		"user": conf["user"],
		"password": conf["password"],
		"driver": conf["driver"]
	}
	query = f"({conf['query']}) AS retail_data"
	try:
		return spark.read.jdbc(url=jdbc_url, table=query, properties=db_properties)
	except Exception as e:
		log_info(e)
		return None


def clean_data(df: DataFrame) -> DataFrame:
	log_info("Preprocessing Data ...")
	df = df.withColumn("InvoiceDate", to_timestamp(col("InvoiceDate"))) \
		.withColumn("Quantity", when(col("Quantity") > 0, col("Quantity")).otherwise(None)) \
		.withColumn("Price", when(col("Price") > 0, col("Price")).otherwise(None))
	return df.dropna(subset=["InvoiceDate", "Quantity", "Price"])


def enrich_data(df: DataFrame) -> DataFrame:
	log_info("Creating parsing columns ...")
	return df.withColumn("Year", year(col("InvoiceDate"))) \
		.withColumn("Month", month(col("InvoiceDate"))) \
		.withColumn("Sales", col("Quantity") * col("Price"))


def analyze_monthly_sales(df: DataFrame) -> DataFrame:
	log_info("Analyzing Sales by Year ......")
	return df.groupBy("Year", "Month") \
		.agg(sum("Sales").alias("TotalSales")) \
		.orderBy("Year", "Month")


def analyze_sales_by_country(df: DataFrame) -> DataFrame:
	log_info("Analyzing Sales by Country ......")
	return df.groupBy("Country") \
		.agg(sum("Sales").alias("TotalSales")) \
		.orderBy(col("TotalSales").desc())


def analyze_avg_sales_per_customer(df: DataFrame) -> DataFrame:
	log_info("Analyzing Average Sales per Customer ......")
	return df.groupBy("Customer ID") \
		.agg(sum("Sales").alias("TotalSales")) \
		.withColumn("AvgSales", col("TotalSales")) \
		.orderBy(col("AvgSales").desc())


def analyze_top10_products(df: DataFrame) -> DataFrame:
	log_info("Analyzing TOP 10 Products by Total Quantity ......")
	return df.groupBy("StockCode") \
		.agg(sum("Quantity").alias("TotalSold")) \
		.orderBy(col("TotalSold").desc()) \
		.limit(10)


def analyze_sales_by_time_slot(df: DataFrame) -> DataFrame:
	log_info("Analyzing Sales by TimeSlot ......")
	df = df.withColumn("Hour", hour(col("InvoiceDate")))
	df = df.withColumn(
		"TimeSlot",
		when((col("Hour") >= 6) & (col("Hour") < 12), "Morning")
		.when((col("Hour") >= 12) & (col("Hour") < 18), "Afternoon")
		.when((col("Hour") >= 18) & (col("Hour") < 24), "Evening")
		.otherwise("Night")
	)
	return df.groupBy("TimeSlot").agg(sum("Sales").alias("TotalSales")).orderBy("TimeSlot")


def save_output(df: DataFrame, output_path: str):
	log_info(f"Saving result → {output_path}")
	df.write.mode("overwrite").parquet(output_path)


def main(useDB: bool = False):

	start = time.time()
	spark = init_spark(useDB=useDB)

	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	csv_path = os.path.join(BASE_DIR, "data", "online_retail.csv")

	if useDB:
		df_raw = load_data_from_db(spark)
	else:
		df_raw = load_data_from_csv(spark, csv_path)

	if df_raw is None:
		log_info("Failed load DataSet. EXIT !")
		return

	df_cleaned = clean_data(df_raw)
	df_enriched = enrich_data(df_cleaned)

	df_result = analyze_monthly_sales(df_enriched)
	save_output(df_result, "output/monthly_sales")

	df_country = analyze_sales_by_country(df_enriched)
	save_output(df_country, "output/sales_by_country")

	df_customer = analyze_avg_sales_per_customer(df_enriched)
	df_customer.show()
	save_output(df_customer, "output/avg_sales_per_customer")

	df_top10 = analyze_top10_products(df_enriched)
	df_top10.show()
	save_output(df_top10, "output/top10_products")

	df_timeslot = analyze_sales_by_time_slot(df_enriched)
	df_timeslot.show()
	save_output(df_timeslot, "output/sales_by_timeslot")

	log_info(f"All Process is done. Turnaround Time: {round(time.time() - start, 2)} sec.")
	spark.stop()


if __name__ == "__main__":
	main(useDB=False)