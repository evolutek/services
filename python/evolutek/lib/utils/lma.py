import concurrent.futures

#############################
# EXECUTE A LIST OF ACTIONS #
#############################
def launch_multiple_actions(tasks):
	launched = []
	with concurrent.futures.ThreadPoolExecutor() as executor:
		for task in tasks:
			launched.append(executor.submit(task.action, *task.args, **task.kwargs))

	results = []
	for action in launched:
		results.append(action.result())
	return results
