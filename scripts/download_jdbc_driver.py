import os
import urllib.request

MYSQL_JAR_URL = "https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.3.0/mysql-connector-java-8.3.0.jar"
JAR_DIR = "jars"
JAR_PATH = os.path.join(JAR_DIR, "mysql-connector-java-8.3.0.jar")

def download_mysql_driver():
    os.makedirs(JAR_DIR, exist_ok=True)
    if os.path.exists(JAR_PATH):
        pass
    else:
        urllib.request.urlretrieve(MYSQL_JAR_URL, JAR_PATH)

