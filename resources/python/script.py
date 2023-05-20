import os
import csv
from lxml import etree
import re
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

def convert_coordinates_to_id(x, y, width):
    return y * width + x

def get_dd_value(tree, dt_text):
    xpath_expression = f"//dl[contains(@class, 'obj-details')]//dt[contains(., '{dt_text}')]/following-sibling::dd[1]/text()"
    dd_element = tree.xpath(xpath_expression)
    return dd_element[0] if dd_element else None

def coords(tree):
    javascript_code = tree.xpath("//script[contains(., 'checkStreetView')]")[0].text

    # Extract the coordinates using a regular expression
    pattern = r"checkStreetView\('([0-9.,]+)'"
    matches = re.findall(pattern, javascript_code)

    if matches:
        return matches[0]
    else:
        return None

def iterate_files(folder_path, csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding = 'utf8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Area", "Number of rooms", "Floor", "Number of floors", "Build year", "Renovation year", "Equipment", "Energy efficiency class", "Location"])  # Header row
        with tqdm(total=len(os.listdir(folder_path)), unit='file(s)') as pbar:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # print(f"File path: {file_path}")

                    # Check if the file is an HTML file
                    if file.endswith('.html') or file.endswith('.htm'):
                        with open(file_path, 'r', encoding='utf8', errors='ignore') as file_obj:
                            file_content = file_obj.read()

                            # Parse the HTML content
                            parser = etree.HTMLParser()
                            tree = etree.fromstring(file_content, parser)

                            row = []

                            area = get_dd_value(tree, 'Area:')
                            number_of_rooms = get_dd_value(tree, 'Number of rooms :')
                            floor = get_dd_value(tree, 'Floor:')
                            no_of_floors = get_dd_value(tree, 'No. of floors:')
                            build_year = get_dd_value(tree, 'Build year:').replace("construction", "").replace("renovation", "")
                            energy_class = get_dd_value(tree, 'Building Energy Efficiency Class:')
                            equipment_value = get_dd_value(tree, 'Equipment:')

                            # Area	Number of rooms	Floor	Number of floors	Build year	Renovation year	Equipment	Energy efficiency class	LocationX	LocationY	Price
                            row.append(float(area.replace("m²", "").strip().replace(',', '.')))

                        # Adding number of rooms
                            row.append(number_of_rooms.strip())

                        # Adding floor
                            row.append(floor.strip())

                        # Adding number of floors
                            row.append(no_of_floors.strip())

                        # Adding building year
                            row.append(build_year.strip().split(',')[0])

                        # Adding renovation year
                            if(',' in build_year):
                                row.append(build_year.strip().split(',')[1])
                            else:
                                row.append("NaN")

                        # Adding equipment
                            equipment = ['Other', 'Foundation', 'Under construction', 'Not equipped', 'Partial decoration', 'Fully equipped']
                            val = "None"
                            if equipment_value is not None:
                                for i in range(len(equipment)):
                                    if(equipment_value.strip() == equipment[i]):
                                        val = str(i)
                                        break
                            row.append(val)
                        
                            ec = "None"
                            if energy_class is not None:
                                ec = energy_class.strip()
                        
                            row.append(ec)
                        
                            c = coords(tree)

                            if c is None:
                                continue
                        # Adding square
                            cc = c.split(",")
                            object_y = float(cc[0])
                            object_x = float(cc[1])
                        
                            #Vilnius city municipality border coordinates
                            x_west = 25.024623
                            x_east = 25.481462
                            y_south = 54.569702
                            y_north = 54.832276

                            # Dividing into 5km2 squares
                            width_step = 0.0885
                            height_step = 0.045

                            city_width = (x_east - x_west) // width_step

                            # Calculating Location
                            object_col = (object_x - x_west) // width_step
                            object_row = (((y_north - object_y) // height_step))*city_width
                            # print(str(int(object_col)) + "_" + str(int(object_row)))
                            idc = convert_coordinates_to_id(object_col, object_row, city_width)
                            row.append(idc)

                            price_xpath_expression = './/span[@class="price-eur"]'
                            price = tree.xpath(price_xpath_expression)[0].text.strip().replace("€", "").replace(" ", "")
                            if "." not in price:
                                price = price + ".00"
                            # row.append(price)
                            writer.writerow(row)
                            pbar.update(1)
                    

# Provide the folder path to iterate through
folder_path = os.getenv("FOLDER_PATH")

# Provide the CSV file path to store the results
csv_file_path = os.getenv("CSV_FILE_PATH")

# Call the function to iterate through files and add lines to the CSV file
iterate_files(folder_path, csv_file_path)
