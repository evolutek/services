import concurrent.futures


#############################
# EXECUTE A LIST OF ACTIONS #
#############################
def launch_multiple_actions(actions, args):
	if len(args) != len(actions):
		return None
	launched = []
	with concurrent.futures.ThreadPoolExecutor() as executor:
		for i in range(len(actions)):
			launched.append(executor.submit(actions[i], *args[i]))
	results = []
	for action in launched:
		results.append(action.result())
	return results
