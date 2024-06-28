from datetime import datetime
import geopandas as gpd

from utilities import read_sql_table_with_geom_cast, backup_dataframe, send_email
from df_operations import check_missing_records, check_missing_records_points
from run_fme import run_fme_environment

# run fme environment to file
run_fme_environment(mode='file')


# Define paths to the geodatabases
gdb_path_points = r"Vertex_Points.gpkg"
gdb_path_lines = r"Vertex_Lines.gpkg"

# Read data from geodatabases
gdf_vertex_points = gpd.read_file(gdb_path_points, layer='FeatureClassPoints')
gdf_vertex_lines = gpd.read_file(gdb_path_lines, layer='FeatureClassLines')

# Column lists for SQL queries
columns_line = ["Object_ID", "GISTable_ID", "ROADNAME", "MeasureFromKM", "MeasureToKM", "MeasureFromMeter", "MeasureToMeter", "FromEasting", "FromNorthing", "ToEasting", "ToNorthing", "DateExported", "ExportedBy", "FMEWorkSpaceUsed"]
columns_point = ["Object_ID", "GIS_RoadSegment_ID", "ROADNAME", "KM_FROM", "KM_TO", "RoadnameTravelDir", "Routes", "Hwy", "CS", "RoadType", "MainRoads", "TRAVELDIR", "Measure", "MeasureMeters", "_element_index", "vertex_number", "Northing", "Easting", "DateCreated"]

# Read data from SQL Server
df_vertex_line_sql = read_sql_table_with_geom_cast('ITOVMW070P', 'Preservation', 'dbo.GIS_VertexLine', columns_line, geom_column="GEOM")
df_vertex_point_sql = read_sql_table_with_geom_cast('ITOVMW070P', 'Preservation', 'dbo.GIS_VertexPoint', columns_point)

# Backup sql data to the database
backup_dataframe(df_vertex_line_sql, 'GIS_VertexLine')
backup_dataframe(df_vertex_point_sql, 'GIS_VertexPoint')


# Generate the full result string
full_result = "\n" * 2 + "**************************Line Comparison**************************\n"
full_result += check_missing_records(gdf_vertex_lines, df_vertex_line_sql, ['ROADNAME', 'MeasureFromKM', 'MeasureToKM'])
full_result += "\n" * 2 + "**************************Point Comparison**************************\n"
full_result += check_missing_records_points(gdf_vertex_points, df_vertex_point_sql, ['ROADNAME', 'Measure'])


send_email(f"The GIS team Made changes to the data {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", full_result, "gostguy3@gmail.com")