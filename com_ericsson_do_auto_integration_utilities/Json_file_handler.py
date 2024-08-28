'''
Created on 15 Aug 2018

@author: emaidns
'''

import json
import zipfile
import shutil
import os
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
import jsonschema
from jsonschema import validate
import yaml
import copy
from xml.dom import minidom

log = Logger.get_logger('Json_file_handler')


class Json_file_handler(object):

    def validate_schema(self, schema_file, user_input_file):
        log.info('validating the file  , ' + user_input_file)

        try:

            with open(schema_file, 'r') as user_input:
                global schema
                schema = json.load(user_input)

        except FileNotFoundError as f:
            log.error('File Not Found Error : Please check the schema file ,' + schema_file)
            assert False

        try:

            with open(user_input_file, 'r') as user_input:

                file_data = json.load(user_input)
                data = [file_data]
                for idx, item in enumerate(data):
                    try:
                        validate(item, schema)

                    except jsonschema.exceptions.ValidationError as ve:
                        log.error(str(ve) + "\n")
                        assert False

        except ValueError as v:
            log.error('please correct the file :' + user_input_file + ' \nERROR : ' + str(v))
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + user_input_file)
            assert False

        log.info('validation done  , ' + user_input_file)

    def update_json_file(self, file_name, json_file_data):

        try:
            with open(file_name, 'w+') as file:

                file.write(json.dumps(json_file_data, sort_keys=False, indent=4))
                log.info('File updated successfully .. ')

        except:
            log.error('Error while updating the json file ,' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def get_json_data(self, file_name):

        try:
            with open(file_name, "r") as jsonFile:
                data = json.load(jsonFile)
                return data

        except ValueError as v:
            log.error('Error while getting data from json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        # IF you want to modify file level attribute in json

    def modify_attribute(self, file_name, attribute, value):

        try:
            with open(file_name, "r") as jsonFile:
                data = json.load(jsonFile)
                data[attribute] = value

            with open(file_name, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def modify_list_of_attributes(self, file_name, attribute_value_dict):

        try:
            with open(file_name, "r") as jsonFile:
                data = json.load(jsonFile)
                for key, value in attribute_value_dict.items():
                    data[key] = value

            with open(file_name, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def modify_nested_list_of_attributes(self, file_name, attribute, attribute_value_dict):

        try:
            with open(file_name, "r") as jsonFile:
                data1 = json.load(jsonFile)
                data = data1[attribute]
                for key, value in attribute_value_dict.items():
                    data[key] = value
            data1[attribute] = data
            with open(file_name, "w") as jsonFile:
                json.dump(data1, jsonFile, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

            # userDefinedData": {

    #   "dataVNFDSpecific": {
    #        "vnfSoftwareVersion": "18.11"
    #                        }
    #                    }
    def modify_nested_dict(self, file_name, first_attr, second_attr, third_attr, value):

        try:
            with open(file_name, "r") as jsonFile:
                data = json.load(jsonFile)
                data[first_attr][second_attr][third_attr] = value

            with open(file_name, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

            # If you want to modify the attribute which is type of

    # "vimZoneConnections": [
    # {
    #      "vimZoneId": "madan12345"
    # }
    # ]
    # attribute = vimZoneConnections , second_attr = vimZoneId , index =0
    def modify_second_level_attr(self, file_name, attribute, index, second_attr, value):

        try:
            with open(file_name, "r") as jsonFile:
                data = json.load(jsonFile)
                tmp = data[attribute]
                tmp[index][second_attr] = value
                data[attribute] = tmp
            with open(file_name, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    # If you want to modify the attribute of type 
    #        userCredentials": {
    #                       "userName": "madan12345",
    #                     }      
    # attribute = userCredentials , second_attr = userName
    def modify_first_level_attr(self, file_name, attribute, second_attr, value):

        try:
            with open(file_name, "r") as jsonFile:
                data = json.load(jsonFile)
                tmp = data[attribute]
                tmp[second_attr] = value
                data[attribute] = tmp
            with open(file_name, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def update_yaml(self, file_name, attribute, value):
        try:
            with open(file_name, "r") as yaml_file:
                data = yaml.load(yaml_file)
                data[attribute] = value

            with open(file_name, "w") as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)

        except ValueError as v:
            log.error('Error while updating the yaml file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def update_second_attr_yaml(self, file_name, attribute1, attribute2, attribute3, value):
        try:
            with open(file_name, "r") as yaml_file:
                data = yaml.load(yaml_file, Loader=yaml.FullLoader)
                data[attribute1][attribute2][attribute3] = value

            with open(file_name, "w") as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)

        except ValueError as v:
            log.error('Error while updating the yaml file: %s: %s', file_name, str(v))
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error: %s', file_name)
            assert False

    def update_third_attr_yaml(self, file_name, attribute1, attribute2, attribute3, value):
        try:

            with open(file_name, "r") as yaml_file:
                data = yaml.load(yaml_file)
                data[attribute1][attribute2][0][attribute3] = value

            with open(file_name, "w") as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)

        except ValueError as v:
            log.error('Error while updating the yaml file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def update_fifth_attr_yaml(self, file_name, attribute1, attribute2, attribute3, attribute4, attribute5, key, value):
        try:

            with open(file_name, "r") as yaml_file:
                data = yaml.load(yaml_file)
                # print(data[attribute1][attribute2][attribute3][attribute4][attribute5][key])
                data[attribute1][attribute2][attribute3][attribute4][attribute5][key] = value
                # print(data[attribute1][attribute2][attribute3][attribute4][attribute5][key])

            with open(file_name, "w") as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)

        except ValueError as v:
            log.error('Error while updating the yaml file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def get_fifth_attr_yaml(self, file_name, attribute1, attribute2, attribute3, attribute4, attribute5, key):
        try:

            with open(file_name, "r") as yaml_file:
                data = yaml.load(yaml_file)
                return data[attribute1][attribute2][attribute3][attribute4][attribute5][key]

        except ValueError as v:
            log.error('Error while updating the yaml file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def modify_third_level_attr(self, file_name, attribute1, attribute2, index, attribute3, value):

        try:
            with open(file_name, "r") as jsonFile:
                data = json.load(jsonFile)
                data[attribute1][attribute2][index][attribute3] = value

            with open(file_name, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def update_nested_dict_yaml(self, file_name, attribute_list, attr, value):
        try:
            with open(file_name, "r") as yaml_file:
                data = yaml.full_load(yaml_file)
                yaml_dict = {}
                new_data = copy.deepcopy(data)
                yaml_dict['data'] = new_data
                for i in range(len(attribute_list)):
                    tmp = new_data[attribute_list[i]]
                    yaml_dict[i] = tmp
                    new_data = tmp
                tmp[attr] = value
                data = yaml_dict['data']
            with open(file_name, "w") as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)

        except ValueError as v:
            log.error('Error while updating the yaml file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def update_st_package(self, package, properties):
        """
        Update service template package
        Input:
        package         : package name with full path
        properties      : list of properties needs to be changed
            [{
                attr_list  : Attributes list,
                attribute  : Attribute name of which value needs to be updated,
                value      : Value
            },]

        Output:
        Creates updated service template package(csar package)
        """
        try:
            zipfilePath, file_name = os.path.split(package)
            zip = zipfile.ZipFile(package)
            file_without_extension = os.path.splitext(file_name)[0]
            unzipped_folder = zipfilePath + '/' + file_without_extension
            log.info('Created temporary folder %s', unzipped_folder)
            log.info('Unzipping the package %s', package)
            zip.extractall(unzipped_folder)
            unzipped_file = unzipped_folder + '/' + file_without_extension + '.yaml'
            for prop in properties:
                self.update_nested_dict_yaml(self, unzipped_file, prop['attr_list'], prop['attribute'], prop['value'])

            shutil.make_archive(unzipped_folder, 'zip', unzipped_folder)
            zipped_st_file = file_without_extension + '.zip'
            log.info('Rename the zip file %s to %s', zipped_st_file, package)
            shutil.move(zipfilePath + '/' + zipped_st_file, package)
            log.info('Remove temporary folder %s', unzipped_folder)
            shutil.rmtree(unzipped_folder)
        except Exception as error:
            log.error('Error while updating the service template :' + package + ' \nERROR : ' + str(error))
            Report_file.add_line('Failed to update the service template :' + package)
            assert False

    def update_any_json_attr(self, file_name, attribute_list, attr, value):

        try:

            with open(file_name, "r") as json_file:
                data = json.load(json_file)
                json_dict = {}
                new_data = copy.deepcopy(data)
                json_dict['data'] = new_data
                tmp = new_data
                for x in attribute_list:
                    tmp = new_data[x]
                    json_dict[x] = tmp
                    new_data = tmp
                tmp[attr] = value
                data = json_dict['data']
            with open(file_name, "w") as json_file:
                json.dump(data, json_file, indent=4, sort_keys=False)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def get_any_attribute_yaml_value(self, file_name, attribute_list, attr):
        try:

            with open(file_name, "r") as yaml_file:
                data = yaml.full_load(yaml_file)
                yaml_dict = {}
                new_data = copy.deepcopy(data)
                yaml_dict['data'] = new_data
                tmp = new_data
                for i in range(len(attribute_list)):
                    tmp = new_data[attribute_list[i]]
                    yaml_dict[i] = tmp
                    new_data = tmp
                return tmp[attr]

        except ValueError as v:
            log.error('Error while updating the yaml file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def get_json_attr_value(self, file_name, attribute):
        log.info('start collecting value for ' + attribute)
        try:
            with open(file_name, 'r') as user_input:
                file_data = json.load(user_input)
                value = file_data[attribute]
                return value
        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            assert False
        log.info('Finished collecting value for  ' + attribute + ' value is ' + value)

    def get_any_json_attr(self, file_name, attribute_list, attr):

        try:

            with open(file_name, "r") as json_file:
                data = json.load(json_file)
                json_dict = {}
                new_data = copy.deepcopy(data)
                json_dict['data'] = new_data
                tmp = new_data
                for x in attribute_list:
                    tmp = new_data[x]
                    json_dict[x] = tmp
                    new_data = tmp
                return tmp[attr]

        except ValueError as v:
            log.error('Error while getting the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

    def modify_xml_attr(self, file_name, tag_name, attr, value):

        try:
            mydoc = minidom.parse(file_name)
            item = mydoc.getElementsByTagName(tag_name)

            item[0]._attrs[attr].value = value

            f = open(file_name, 'w+')
            mydoc.writexml(f)

        except ValueError as v:
            log.error('Error while updating the json file :' + file_name + ' \nERROR : ' + str(v))
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + file_name)
            log.error('Script terminated due to error printed above ')
            Report_file.add_line('Script terminated due to error in Json_file_handler')
            assert False
