# @Author Jason Cronqusit 

import requests
import os
import threading
from queue import Queue
import time
import re

def get_urls():
  with open("urls", "r") as host_file:
    urls = [ url.strip() for url in iter(host_file) ]
    return urls
   print("Error: Could not load URLs" )
   return []
   
def f_download(url):
  try:
    log_connection = requests.get(url, timeout = 2.5)
    return (log_connection.text)
  except:
    return("")
    
def f_write(url, log_text):
  filename = url.split('/')[-1]
  with open('./logs/{}'.format(filename), 'w') as fp:
    fp.write(url + "\n\n" + log_text)
    return True
  return False
  
class Workers:
  thread_count=40
  run=True
  
  download_queue = Queue()
  
  threads = {}
  classifiers = {
    'classifier_name': 'value to look for in log'
  }
  
  def __init__(self, urls):
    self._stop_event = threading.Event()
    threads_all = self.make_workers(self.thread_count)
    for url in urls:
      self.download_queue.put(url)
    print("waiting for download_queue.join()")
    self.downlaod_queue.join()
    print("waiting for save_queue.join()")
    self.save_queue.join()
    print("waiting for all thread.join()")
    self.kill_workers(threads_all)
    
  def get_worker_config(self):
    return {
      'download':{
        'num_threads':50,
        'func': self.worker_downlaod,
        'source': self.download_queue
      },
      'classify':{
        'num_threads': 20,
        'func': self.worker_classify,
        'source': self.save_queue
      }
    }
    
  def worker_download(self):
    while not self._stop_event.is_set():
      url = self.download_queue.get()
      if url is not None:
        self.save_queue.put((url, f_download(url)))
      self.download_queue.task_done()
      
  def worker_classify(self):
    while not self._stop_event.is_set()
      try:
        url, text = self.save_queue.get(block=True, timeout=5)
        if url is not None:
          for class_name, classifier in self.classifiers.items():
            if re.search(classifier, text):
              with open('logs/{}'.format(class_name), 'a') as w_file:
                w_file.write('{}\n'.format(url))
        self.save_queue.task_done()
      except:
        thread_log("timeout")
  
  def worker_save(self):
    while not self._stop_event.is_set():
      url, text = self.save_queue.get()
      if url is not None:
        f_write(url, text)
        self.save_queue.task_done()
        
  def queue_status(self):
    while not self._stop_event.is_set():
      print("download: {}".format(self.download_queue.qsize()) )
      print("classify: {}".format(self.save_queue.qsize()) )
      time.sleep(1)
      
  def make_workers(self, num_threads):
    config = self.get_worker_config()
    for name, worker in config.items():
      self.threads[name] = [ threading.Thread( target=worker['func']) for i in range(worker['num_threasd']) ]
    self.status_thread = threading.Thread( target=self.queue_status )
    
    for thread_name, thread_array in self.threads.items():
      for thread in thread_array:
        thread.start()
    
    self.status_thread.start()
    
    return [self.status_thread]
    
  def kill_workers(self, threads):
    print("Killing Threads")
    self._stop_event.set()
    for thread_name, thread_config in self.get_worker_config().items():
      for i in range(thread_config['num_threads']):
        thread_config['source'].put(None)
      for thread in self.threads[thread_name]:
        thread.join()
        
if "logs" not in os.listdir():
  os.mkdir("logs")
print("Starting Download")
workers = Workers(get_urls())
print("Download Complete")

  
