
movements.csv: data_processing/extract_results.py data_processing/common.py data/usakpress.db
	python data_processing/extract_results.py data/usakpress.db

move_sum.move.csv move_sum.sup.csv: movements.csv
	python data_processing/summarize_movements.py movements.csv images/map_countries.csv move_sum

supports.pdf moves.pdf:
	Rscript visualization/draw_maps.R

p2pmessages:
	mkdir -p press_data
	python data_processing/save_messages.py data/usakpress.db
	python data_processing/deduplicate.py press_data

standardize_results:
	mkdir -p data_standardized
	python data_processing/standardize_results_usak.py
	python data_processing/standardize_results_usdp.py