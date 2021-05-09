#!/home/pi/Python-3.9.4/install/bin/python3

import os
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import datetime
import time
import traceback
import create_visualization

cloudURL = "cloud.your-domain.com"
usr = "Secret"
passwd = "Password"

def get_latency():
  # execute ping command
  try:
    stdout = subprocess.check_output(["ping", "pingserver.com", "-c", "5", "-i", "0.2"])
  except:
    traceback.print_exc()
    return (None,None)
  
  #parse result
  line1 = [x for x in stdout.decode('utf-8').split('\n') if x.find('packet loss') != -1][0]
  line2 = [x for x in stdout.decode('utf-8').split('\n') if x.find('min/avg') != -1][0]
  #print("line1: \n{}\n".format(line1))
  #print("line2: \n{}\n".format(line2))

  packetloss = float(line1.split('%')[0].split(' ')[-1])
  latency = float(line2.split('/')[4])

  return (packetloss, latency)
  #print("packetloss : {}".format(packetloss))
  #print("latency: {}".format(latency))

def get_uplink_downlink():
  try:
    stdout = subprocess.check_output(["speedtest-cli", "--csv"])
  except:
    traceback.print_exc()
    return (0,0)
    #return (None,None)
  #print("stdout:\n{}\n".format(stdout))

  # parse result
  uplink = float(stdout.decode('utf-8').split(',')[7]) / 1e6
  downlink = float(stdout.decode('utf-8').split(',')[6]) / 1e6
  
  return (uplink,downlink)

print("starting ping.py")

# file names
log_filename = "/mnt/ramdisk/log.csv"
plot_latency_filename = "/mnt/ramdisk/plot_latency.png"
plot_uplink_filename = "/mnt/ramdisk/plot_uplink.png"
plot_downlink_filename = "/mnt/ramdisk/plot_downlink.png"

# initalize empty lists
latency_list = []
t_list = []
uplink_list = []
downlink_list = []
previous_latency_cloud_filename = None
previous_uplink_cloud_filename = None
previous_downlink_cloud_filename = None

# main infinite loop
while True:
  
  # wait
  time.sleep(60)

  # do not do measurements on Sundays 9:00 - 10:59
  now = datetime.datetime.now()
  if now.weekday() == 6 and (now.hour == 9 or now.hour == 10):
    continue

  # execute ping
  (packetloss, latency) = get_latency()

  # execute speedtest
  (uplink, downlink) = get_uplink_downlink()

  # store values
  if latency is not None and uplink is not None and downlink is not None:
    t_list.append(datetime.datetime.now())
    latency_list.append(latency)
    uplink_list.append(uplink)
    downlink_list.append(downlink)

    # append values to log file
    file_sent = False
    with open(log_filename, "a") as f:
      # append line to log file
      f.write("{};{};{};{};{}\n".
              format(datetime.datetime.now().timestamp(), packetloss, latency, uplink, downlink))
      print("{} packet loss: {} %, latency: {} ms, uplink: {} MBit/s, downlink: {} MBit/s".
              format(datetime.datetime.now().strftime("%H:%M:%S"),
                     packetloss, latency, uplink, downlink))
   
  # depending on current time, upload file
  now = datetime.datetime.now()
  if now.minute <= 2:
    if not file_sent:
    
      file_sent = True

      # login to owncloud  
      import owncloud
      oc = owncloud.Client('cloud.your-domain.com')
      oc.login('username', 'password')
  
      # upload log file
      cloud_filename = "log/{}.csv".format(now.strftime("%Y_%m_%d_%H:%M:%S"))
      oc.put_file(cloud_filename, log_filename)
      print("File \"{}\" sent".format(cloud_filename))
      os.remove(log_filename)
      time.sleep(1)
      with open(log_filename, "w") as f:
        f.write("# timestamp;pack loss (%);latency (ms);uplink (MBit/s);downlink (MBit/s)\n")

      # create visualization
      try:
        # latency plot
        color_levels = [0, 25, 50, 100, 10000]
        ylabel = "Latenz [ms]"
        create_visualization.create_plot(t_list, latency_list, plot_latency_filename, color_levels, ylabel, False)
  
        # send plot file to nextcloud
        time.sleep(2)
        cloud_filename = "plot/{}_latency.png".format(now.strftime("%Y_%m_%d_%H:%M:%S"))
        oc = owncloud.Client('https://cloud.your-domain.com')
        oc.login('username', 'password')
        oc.put_file(cloud_filename, plot_latency_filename)
        print("File \"{}\" sent".format(cloud_filename))
        
        # delete previous plot file on the cloud
        if previous_latency_cloud_filename:
          oc.delete(previous_latency_cloud_filename)
        previous_latency_cloud_filename = cloud_filename
      except:
        traceback.print_exc()
        pass
  
        
      try:
        # uplink plot
        color_levels = [0, 5, 10, 15, 200]
        ylabel = "Uplink [MBit/s]"
        create_visualization.create_plot(t_list, uplink_list, plot_uplink_filename, color_levels, ylabel, True)
  
        # send plot file to nextcloud
        time.sleep(2)
        cloud_filename = "plot/{}_uplink.png".format(now.strftime("%Y_%m_%d_%H:%M:%S"))
        oc = owncloud.Client('https://cloud.your-domain.com')
        oc.login('username', 'password')
        oc.put_file(cloud_filename, plot_uplink_filename)
        print("File \"{}\" sent".format(cloud_filename))
        
        # delete previous plot file on the cloud
        if previous_uplink_cloud_filename:
          oc.delete(previous_uplink_cloud_filename)
        previous_uplink_cloud_filename = cloud_filename
      except:
        traceback.print_exc()
        pass
  
        
      try:
        # downlink plot
        color_levels = [0, 15, 30, 40, 200]
        ylabel = "Downlink [MBit/s]"
        create_visualization.create_plot(t_list, downlink_list, plot_downlink_filename, color_levels, ylabel, True)
  
        # send plot file to nextcloud
        time.sleep(2)
        cloud_filename = "plot/{}_downlink.png".format(now.strftime("%Y_%m_%d_%H:%M:%S"))
        oc = owncloud.Client('https://cloud.your-domain.com')
        oc.login('username', 'password')
        oc.put_file(cloud_filename, plot_downlink_filename)
        print("File \"{}\" sent".format(cloud_filename))
        
        # delete previous plot file on the cloud
        if previous_downlink_cloud_filename:
          oc.delete(previous_downlink_cloud_filename)
        previous_downlink_cloud_filename = cloud_filename
      except:
        traceback.print_exc()
        pass

  else:
    file_sent = False

