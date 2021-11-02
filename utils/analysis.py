import json
import os
import glob
import logging
logging.basicConfig(level=logging.INFO)

def load_database():
  db_entries = []
  files = glob.glob("./dynamodb/*.json")
  for file_name in files:
    with open(file_name) as file:
      for line in file:
        entry = json.loads(line)
        form_submission = json.loads(entry["Item"]["FormSubmission"]["S"])
        db_entries.append(form_submission["2"])

  return db_entries

def load_file(file):
  input_file = open(file, "r")
  input_content= json.load(input_file)
  input_file.close()
  return input_content

def checkIfDuplicates(listOfElems):
    ''' Check if given list contains any duplicates '''
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        return True

### Main
if __name__ == "__main__":
  form_submissions = load_database()
  thread_results = load_file("threads_output.json")
  agg_results = load_file("aggregated_results.json")

  form_input = {"success":[], "failed":[]}

  for thread in thread_results["threads"]:
    form_input["success"].extend(thread["form_input"]["success"])
    form_input["failed"].extend(thread["form_input"]["failed"])

  if len(thread_results["threads"]) != agg_results["lambda_invocations"]:
    logging.warning(f"Only {len(thread_results['threads'])} reported back out of {agg_results['lambda_invocations']}")
    logging.warning("Results are not accurate")
  else:
    logging.info(f"All {agg_results['lambda_invocations']} lambda invocations reported back sucessfully.")

  forms_succeeded = 0
  forms_multiple = 0
  forms_failed = 0
  forms_incognito = 0
  forms_dropped = 0

  logging.info("Starting Analysis")
  completion = 0
  total_entries = len(form_input["failed"]) + len(form_input["success"])
  processed_entries = 0

  logging.info(f"Total entries in dynamodb: {len(form_submissions)}")
  logging.info(f"Total submissions sent: {total_entries}")

  def checking_completion(comp):
    completed = int((processed_entries/total_entries)*100)
    if completed > comp:
      logging.info(f"{completed}%")
      return completed
    else:
      return comp


  for input in form_input["success"]:
    processed_entries += 1
    completion = checking_completion(completion)

    instances = 0
    for form in form_submissions:
      if input == form:
        instances += 1
    
    if instances < 1:
      # print(f"Submission with uuid: {input} was not saved in the vault")
      forms_dropped += 1
    elif instances > 1:
      # print(f"Submission with uuid: {input} was found multiple times in the vault")
      forms_multiple += 1
    else:
      forms_succeeded += 1

  for input in form_input["failed"]:
    processed_entries += 1
    completion = checking_completion(completion)
    
    instances = 0
    for form in form_submissions:
      
      if input == form:
        instances += 1
    
    if instances > 0:
      forms_incognito +=0
    else:
      forms_failed += 1

  if checkIfDuplicates(form_submissions):
    logging.info("Duplicate submissions found in vault")
  else:
    logging.info("No duplicate submissisons found in vault")
  
  print("=========================================================================")
  print(f"Successfull: {forms_succeeded}, Failed with Client aware: {forms_failed}")
  print(f"Dropped without warning: {forms_dropped}, Stored without warning: {forms_incognito}")
  print(f"Forms with multiple submissions: {forms_multiple}")
  print(f"Total Failure %: {int(sum([forms_failed, forms_dropped])/total_entries*100)}%")
  print(f"Good (client notified) Failure %: {int(forms_failed/total_entries*100)}%")
  print(f"Bad (lost in ether) Failure %: {int(forms_dropped/total_entries*100)}%")
  print("=========================================================================")