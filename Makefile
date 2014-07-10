
movements.csv: data_processing/extract_results.py data_processing/common.py data/usakpress.db
	python data_processing/extract_results.py data/usakpress.db

p2pmessages:
	mkdir -p press_data
	python data_processing/save_messages.py data/usakpress.db
	python data_processing/deduplicate.py press_data
