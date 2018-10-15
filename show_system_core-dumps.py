import yaml
from pprint import pprint as pp
import jnpr.junos.exception
from jnpr.junos import Device
import re
import csv
from datetime import datetime
from lxml import etree

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

now = datetime.now()
cdt_string = now.strftime("%d-%m-%Y-%H-%M-%S")


def main():
    """Main function."""
    print("Starting script..")

    f_name = "show_system_core_dumps-" + cdt_string + ".csv"

    with open(f_name, mode='w') as employee_file:
        csv_writer = csv.writer(employee_file,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["Hostame", "Member", "File Name", "File Size", "File Date"])

        for host in config['hosts']:

            msg = ("Connecting to host:{}, ip address:{}"
                   .format(host['hostname'], host['hostname']))
            print(msg)

            try:
                    dev = Device(user=host['username'],
                                 host=host['hostname'],
                                 password=host['password'],
                                 port=22)
                    dev.open()

            except jnpr.junos.exception.ProbeError as err:
                print(err)

            except jnpr.junos.exception.ConnectAuthError as err:
                print(err)

            else:
                dev.timeout = 60
                result = dev.rpc.get_system_core_dumps()

                core_dumps = parse_files(host['hostname'], result)
                for item in core_dumps:
                    csv_writer.writerow(item)
                dev.close()


def get_details(host, re_name, file):

    file_name = file.findtext('.//file-name')
    file_size = file.findtext('.//file-size')
    file_date = int(file.findtext('.//file-date'))
    print(file_name, file_size, file_date)
    file_date = datetime.utcfromtimestamp(file_date).strftime('%d-%m-%Y %H:%M:%S')
    parsed = [host, re_name, file_name, file_size, file_date]

    return parsed


def parse_files(host, result):
    core_dumps = []
    routing_engines = result.findall(".//multi-routing-engine-item")
    if len(routing_engines) == 0:
            files_info = result.findall(".//file-information")
            for file in files_info:
                core_dumps.append(get_details(host, "master-re", file))

    else:
        print("multi re")
        for routing_engine in routing_engines:
            re_name = routing_engine.findtext('re-name')
            files_info = routing_engine.findall(".//file-information")
            for file in files_info:
                core_dumps.append(get_details(host, re_name, file))



    return core_dumps

if __name__ == "__main__":
    main()