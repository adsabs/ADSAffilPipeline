scp ads@adsset:/proj/ads_abstracts/config/affils/Affiliations_all.tsv ./affils_CSG_raw.tsv
scp ads@adsset:/proj/ads_abstracts/config/affils/parent_child_facet_inst.tsv ./pc_facet_CSG_raw.tsv
python convert_encoding.py affils_CSG_raw.tsv > affils_ascii.tsv
python convert_encoding.py pc_facet_CSG_raw.tsv > pc_facet_ascii.tsv
python splitter.py affils_ascii.tsv
ls -p |grep '\/'
echo 'go make edits if there are any directories other than [A1-9]'
python check_format.py
echo 'go make edits if check_format produced output!'

# python addpc_to_splits.py
# python word_counter.py
# cat */*.count | sort > learning_model.dat
# cp learning_model.dat ../config
# cp pc_facet_ascii.tsv ../config/parent_child_facet_inst.tsv
