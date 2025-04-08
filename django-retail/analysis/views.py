import os
import pandas as pd
from django.shortcuts import render

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_monthly_sales(request):	
	parquet_path = os.path.join(base_dir, "output", "monthly_sales")
	df = pd.read_parquet(parquet_path).sort_values(by=["Year", "Month"])
	return render_table(request, df, "Monthly Sales")

def show_sales_by_country(request):
	parquet_path = os.path.join(base_dir, "output", "sales_by_country")
	df = pd.read_parquet(parquet_path).sort_values(by="TotalSales", ascending=False)
	return render_table(request, df, "Sales by Country")

def show_avg_sales_per_customer(request):
	parquet_path = os.path.join(base_dir, "output", "avg_sales_per_customer")
	df = pd.read_parquet(parquet_path).sort_values(by="AvgSales", ascending=False)
	return render_table(request, df, "Average Sales per Customer")

def show_top10_products(request):
	parquet_path = os.path.join(base_dir, "output", "top10_products")
	df = pd.read_parquet(parquet_path).sort_values(by="TotalSold", ascending=False)
	return render_table(request, df, "Top 10 Products by Quantity")

def show_sales_by_timeslot(request):
	parquet_path = os.path.join(base_dir, "output", "sales_by_timeslot")
	df = pd.read_parquet(parquet_path)
	return render_table(request, df, "Sales by TimeSlot")

# 공통 렌더링 함수
def render_table(request, df: pd.DataFrame, title: str):
	context = {
		"title": title,
		"columns": df.columns,
		"rows": df.to_dict(orient="records")
	}
	return render(request, "analysis/result_table.html", context)
