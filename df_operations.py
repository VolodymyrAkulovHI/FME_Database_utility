########################################################################################################################
####################################### LINES ##########################################################################
########################################################################################################################

def check_missing_records(df1, df2, id_columns):
    """
    Check for missing records between two dataframes based on specified ID columns and 
    return them in a nice formated string.

    Parameters:
    df1 (DataFrame): First dataframe to compare.
    df2 (DataFrame): Second dataframe to compare.
    id_columns (list): List of column names to use for identifying records.

    Returns:
    str: Categorized summary of missing and adjusted segments between the dataframes.
    """
    def group_segments(records):
        
        # add all roads with the same roadname into a dict
        grouped = {}
        for record in records:
            roadname = record['ROADNAME']
            from_km = record['MeasureFromKM']
            to_km = record['MeasureToKM']
            if roadname not in grouped:
                grouped[roadname] = []
            grouped[roadname].append((from_km, to_km))


        merged_records = {}
        
        # iterate over every unique roadname
        for roadname, segments in grouped.items():
            
            # init some stuff for grouping roads together: keep track of start and end as well as # of segments 
            segments.sort()
            merged_segments = []
            current_start, current_end = segments[0]
            segment_count = 1

            # iterate on amount of segments with this roadname
            for i in range(1, len(segments)):
                # get the next set of start and end coords
                next_start, next_end = segments[i]

                # if the next line intersects or is on the edge of our current line then merge it in and adjust
                # the end coordinate of that line if its further
                if next_start <= current_end:
                    current_end = max(current_end, next_end)
                    segment_count += 1
                else:
                    # otherwise reset because this is the start of a new segment of road further down the cs
                    merged_segments.append((current_start, current_end, segment_count))
                    current_start, current_end = next_start, next_end
                    segment_count = 1

            # finish by adding the last segement for the current road and adding the current road to the overall list
            merged_segments.append((current_start, current_end, segment_count))
            merged_records[roadname] = merged_segments
        
        # when we finish the loop we should have a dictionary of lists of all the roads
        return merged_records

    # Create sets for comparison
    set1 = set(df1[id_columns].itertuples(index=False, name=None))
    set2 = set(df2[id_columns].itertuples(index=False, name=None))

    # find the differences between the two by subtracting the sets
    missing_in_df1 = set2 - set1
    missing_in_df2 = set1 - set2

    # pull all the records that were missing from the dataframe for processing
    missing_records_in_sql = _extract_records(df2, missing_in_df1, id_columns)
    missing_records_in_fme = _extract_records(df1, missing_in_df2, id_columns)


    # group the segments so were not dealing with a million segments and instead the roads themselves
    grouped_missing_in_sql = group_segments(missing_records_in_sql)
    grouped_missing_in_fme = group_segments(missing_records_in_fme)


    # Define the categories of segment discreptincies
    categorized_segments = {
        'Segments added to or removed from existing section': [],       # Diffrent number of segments, Same or similar bounds
        'Segments have been adjusted or moved': [],                     # Same number of segmets, Diffrent bounds
        'Segments that had internal bounds adjusted': [],               # Same number of segmens, Same bounds
        'Segments removed from database': [],                
        'Segments added to database': []
    }

    # find the ones the roads that are missing in both
    intersecting_roadnames = set(grouped_missing_in_sql.keys()).intersection(grouped_missing_in_fme.keys())


    for roadname in intersecting_roadnames:
        # for every grouped segment of road on that road we need to compare to tthe opposite side to check if theyre simillar
        for segment_removed in grouped_missing_in_sql[roadname]:
            best_match = None
            min_distance = float('inf')

            for segment_added in grouped_missing_in_fme[roadname]:
                start_distance = abs(segment_removed[0] - segment_added[0])
                end_distance = abs(segment_removed[1] - segment_added[1])
                total_distance = start_distance + end_distance

                if total_distance < min_distance and start_distance <= 0.1 and end_distance <= 0.3:
                    min_distance = total_distance
                    best_match = (segment_added, start_distance, end_distance)

            if best_match:
                segment_added, start_distance, end_distance = best_match
                desc = f"{roadname}-{segment_removed[0]:.5f}-{segment_removed[1]:.5f} segments: {segment_removed[2]} --> {roadname}-{segment_added[0]:.5f}-{segment_added[1]:.5f} segments: {segment_added[2]}"
                if segment_removed[2] != segment_added[2]:
                    categorized_segments['Segments added to or removed from existing section'].append(desc)
                elif start_distance != 0 or end_distance != 0:
                    categorized_segments['Segments have been adjusted or moved'].append(desc)
                else:
                    categorized_segments['Segments that had internal bounds adjusted'].append(desc)

    _categorize_changes(grouped_missing_in_sql, intersecting_roadnames, False, 'Segments removed from database', categorized_segments)
    _categorize_changes(grouped_missing_in_fme, intersecting_roadnames, False, 'Segments added to database', categorized_segments)


    return _unpack_categories(categorized_segments)

########################################################################################################################
####################################### POINTS #########################################################################
########################################################################################################################

def check_missing_records_points(df1, df2, id_columns):
    """
    Check for missing records between two dataframes based on specified ID columns and 
    return them in a nicely formatted string.

    Parameters:
    df1 (DataFrame): First dataframe to compare.
    df2 (DataFrame): Second dataframe to compare.
    id_columns (list): List of column names to use for identifying records.

    Returns:
    str: Categorized summary of missing and adjusted points between the dataframes.
    """
    def group_points(records):
        # Add all roads with the same roadname into a dict
        grouped = {}
        for record in records:
            roadname = record['ROADNAME']
            atkm = record['Measure']
            if roadname not in grouped:
                grouped[roadname] = []
            grouped[roadname].append(float(atkm))  # Ensure the measure is a float

        merged_records = {}
        
        # Iterate over every unique roadname
        for roadname, points in grouped.items():
            # Sort the points
            points.sort()
            merged_points = []
            current_start = points[0]
            current_end = points[0]
            point_count = 1

            # Iterate over points to group them based on proximity
            for i in range(1, len(points)):
                next_point = points[i]
                if next_point - current_end <= 5:
                    current_end = next_point
                    point_count += 1
                else:
                    merged_points.append((current_start, current_end, point_count))
                    current_start = next_point
                    current_end = next_point
                    point_count = 1

            # Finish by adding the last group of points
            merged_points.append((current_start, current_end, point_count))
            merged_records[roadname] = merged_points

        return merged_records



    # Apply the function to your DataFrame columns
    df1['Measure'] = df1['Measure'].astype(float).round(5)
    df2['Measure'] = df2['Measure'].astype(float).round(5)

    # Create sets for comparison
    set1 = set(df1[id_columns].itertuples(index=False, name=None))
    set2 = set(df2[id_columns].itertuples(index=False, name=None))

    # Find the differences between the two by subtracting the sets
    missing_in_df1 = set2 - set1
    missing_in_df2 = set1 - set2

    # Pull all the records that were missing from the dataframe for processing
    missing_records_in_sql = _extract_records(df2, missing_in_df1, id_columns)
    missing_records_in_fme = _extract_records(df1, missing_in_df2, id_columns)

    # Group the points so we're not dealing with a million individual points but instead grouped by roadnames
    grouped_missing_in_sql = group_points(missing_records_in_sql)
    grouped_missing_in_fme = group_points(missing_records_in_fme)

    # Define the categories of point discrepancies
    categorized_points = {
        'Points added to or removed from existing section': [],
        'Points have been adjusted or moved': [],
        'Points that had internal bounds adjusted': [],
        'Points removed from database': [],                
        'Points added to database': []
    }

    # Find the roadnames that are missing in both
    intersecting_roadnames = set(grouped_missing_in_sql.keys()).intersection(grouped_missing_in_fme.keys())

    for roadname in intersecting_roadnames:
        # For every grouped point on that road, compare to the opposite side to check if they are similar
        for point_removed in grouped_missing_in_sql[roadname]:
            best_match = None
            min_distance = float('inf')

            for point_added in grouped_missing_in_fme[roadname]:
                # Extract the start, end, and count values
                point_removed_start, point_removed_end, point_removed_count = point_removed
                point_added_start, point_added_end, point_added_count = point_added

                start_distance = abs(point_removed_start - point_added_start)
                end_distance = abs(point_removed_end - point_added_end)
                total_distance = start_distance + end_distance

                if total_distance < min_distance and start_distance <= 5 and end_distance <= 5:
                    min_distance = total_distance
                    best_match = (point_added, start_distance, end_distance)

            if best_match:
                point_added, start_distance, end_distance = best_match
                if (start_distance <= 0.002 and start_distance > 0) or (end_distance <= 0.002 and end_distance > 0):
                    continue  # Skip this match if the distance is non-zero and <= 0.02
                desc = (f"{roadname} {point_removed_start:.5f}-{point_removed_end:.5f} points: {point_removed_count} "
                        f"--> {roadname} {point_added_start:.5f}-{point_added_end:.5f} points: {point_added_count}")
                if point_removed_count != point_added_count:
                    categorized_points['Points added to or removed from existing section'].append(desc)
                elif start_distance != 0 or end_distance != 0:
                    categorized_points['Points have been adjusted or moved'].append(desc)
                else:
                    categorized_points['Points that had internal bounds adjusted'].append(desc)

    categorized_points = {'Points removed from database': [], 'Points added to database': []}

    _categorize_changes(grouped_missing_in_sql, intersecting_roadnames, True, 'Points removed from database', categorized_points)
    _categorize_changes(grouped_missing_in_fme, intersecting_roadnames, True, 'Points added to database', categorized_points)

    return _unpack_categories(categorized_points)

########################################################################################################################
####################################### HELPERS ########################################################################
########################################################################################################################

def _extract_records(df, ids, id_columns):
        # Convert the list of IDs to a set for faster membership checking
        ids = set(ids)
        
        # Set the dataframe index to the specified ID columns
        df_indexed = df.set_index(id_columns)
        
        # Create a mask to identify rows where the index is in the set of IDs
        mask = df_indexed.index.isin(ids)
        
        # Filter the dataframe using the mask, reset the index, and convert to a list of dictionaries
        return df_indexed[mask].reset_index().to_dict('records')

def _categorize_changes(grouped_missing, intersecting_roadnames, points, category, categorized_dict):
    description_format = "{} {:.5f}-{:.5f} points: {}" if points else "{}-{:.5f}-{:.5f} segments: {}"
    
    for roadname in set(grouped_missing.keys()) - intersecting_roadnames:
        for item in grouped_missing[roadname]:
            desc = description_format.format(roadname, item[0], item[1], item[2])
            categorized_dict[category].append(desc)

def _unpack_categories(categorized_dict):
    result = ""
    for category, items in categorized_dict.items():
        if items:
            result += f"\n\n{category}:\n" + "\n".join(items)
        else:
            result += f"\n\nNo {category.lower()}.\n"
    return result
