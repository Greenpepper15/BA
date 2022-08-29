#In the ODIN_II SRC directory call the following cmds to generate log files:

odin_src_2012_to_2015.log:

git log --all --numstat --date=short --after=2012-6-1 --before=2015-12-31  --pretty=format:--%h--%ad--%aN --no-renames -- .  > odin_src_2012_to_2015.log

odin_src_2016_to_2018.log:

git log --all --numstat --date=short --after=2016-1-1 --before=2018-12-31  --pretty=format:--%h--%ad--%aN --no-renames -- .  > odin_src_2015_to_2018.log

odin_src_2019_to_2022.log:

git log --all --numstat --date=short --after=2019-1-1 --before=2022-6-2  --pretty=format:--%h--%ad--%aN --no-renames -- .  > odin_src_2019_to_2022.log

odin_scr_2012_to_2022.log:

git log --all --numstat --date=short --after=2012-6-1 --before=2022-6-2  --pretty=format:--%h--%ad--%aN --no-renames -- .  > odin_src_2012_to_2022.log

odin_src_2012_to_2022_with_msg.log

git log --all --numstat --date=short --after=2012-6-1 --before=2022-6-2  --pretty=format:--%h--%ad--%aN--%s --no-renames -- . > odin_src_2012_to_2022_with_msg.log

odin_scr_2012_to_2022_with_parent:

git log --all --numstat --date=short --after=2012-6-1 --before=2022-6-2  --pretty=format:--%h--%ad--%aN--%P --no-renames -- . > odin_scr_2012_to_2022_with_parent.log


#To to parse the log files into a .json format which are used in the Jupyter Notebooks

For example to parse odin_src_2012_to_2022_with_msg.log to odin_scr_2012_to_2022_with_msg.json
we need to use the parse_git_log.py script in the data_collection_script.
You may need to alter a few lines to use it.

[Here is the parse script](../../../data_collection_scripts/parse_git_log.py)

#A .csv file in this folder if created after applying code-maat to a .log file.

