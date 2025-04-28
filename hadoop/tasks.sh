#!/bin/bash

# Инициализация HDFS
hdfs namenode -format -force
start-dfs.sh
start-yarn.sh

# Дайте сервисам время на запуск
sleep 10

# 1. Создание директории
hdfs dfs -mkdir -p /createme || echo "Не удалось создать /createme"

# 2. Удаление директории
hdfs dfs -mkdir -p /delme && hdfs dfs -rm -r /delme || echo "Не удалось удалить /delme"

# 3. Создание файла
echo "Это пример содержимого файла" | hdfs dfs -put - /nonnull.txt || echo "Не удалось создать файл"

# 4. WordCount
hdfs dfs -put /opt/shadow.txt /shadow.txt || echo "Не удалось загрузить shadow.txt"
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /shadow.txt /wordcount-output || echo "Не удалось выполнить WordCount"

# 5. Подсчет Innsmouth
hdfs dfs -cat /wordcount-output/part-r-00000 | grep -w "Innsmouth" | awk '{print $2}' | hdfs dfs -put - /whataboutinsmouth.txt || echo "0" | hdfs dfs -put - /whataboutinsmouth.txt

# Вывод результатов
echo "===== Результаты ====="
hdfs dfs -ls /
hdfs dfs -cat /whataboutinsmouth.txt