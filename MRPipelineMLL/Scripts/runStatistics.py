import Utility.config as config
from Statistics.shapeAnalyser import ShapeAnalyser
from Statistics.shapeStatistics import ShapeStatistics
config.initialize()

sa = ShapeAnalyser()
ss = ShapeStatistics()
#rows = sa.analyse_shapes(folder="Data\\OriginalShapeDatabase")
#sa.save_analysis(rows, file_name = "data_info.csv")

# ss.retrieve_data(rows, file_name = "data_info.csv")
# ss.show_statistics(folder="Data\\DataAnalysis\\OriginalDataStatistics")


norm_rows = sa.analyse_shapes(folder="Data\\NormalizedShapeDatabase")
sa.save_analysis(norm_rows, file_name = "normalized_data_info.csv")

ss.retrieve_data(file_name="normalized_data_info.csv")
ss.show_statistics(folder="Data\\DataAnalysis\\NormalizedDataStatistics")

