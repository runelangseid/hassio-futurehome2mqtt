import sys
import time

import pyfimptoha.client as fimp


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print(
            'Usage: \n"python run.py" to fetch data from FIMP and push components to Home Assistant'
        )
    else:
        print('Starting service...')
        f = fimp.Client()
        print('Sleeping forever...')

        while True:
            if not f.connected:
                print("MQTT client: No longer connected... Exiting")
                break
            time.sleep(20)
