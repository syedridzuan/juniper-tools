import yaml
from pprint import pprint as pp
import jnpr.junos.exception
from jnpr.junos import Device
import re
import csv
from datetime import datetime

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

now = datetime.now()
cdt_string = now.strftime("%d-%m-%Y-%H-%M-%S")


def main():
    """Main function."""
    print("Starting script..")

    f_name = "show_version-" + cdt_string + ".csv"

    with open(f_name, mode='w') as employee_file:
        csv_writer = csv.writer(employee_file,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["Hostname", "Version", "Model"])

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
                result = dev.rpc.get_software_information()
                version = result.findtext(".//junos-version")
                model = result.findtext(".//product-model")

                if version:
                    pass
                else:
                    s = result.find(".//package-information").findtext("comment")
                    version = re.search(r'\[(.*?)\]', s).group(1)

                csv_writer.writerow([host['hostname'], version, model])

            dev.close()


if __name__ == "__main__":
    main()
