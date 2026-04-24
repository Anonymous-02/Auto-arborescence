import os, csv, re
os.chdir(__file__ + "\\..")
files = [i for i in os.listdir() if i.endswith('.csv')]
name = {i:i.split("_")[-1].split(".")[0] for i in files}
tree = {}
nomenclature = {}
for f in files:
	temp = []
	nomenclature[name[f]] = []
	with open(os.getcwd() +"/" + f,"r", newline="") as file:
		temp = list(csv.reader(file, delimiter=";"))
		temp.pop(0)
	mt = True
	while mt:
		for j in range(len(temp[-1])):
			if temp[-1][j] != "":
				mt = False
		if mt:
			temp.pop(-1)
	xlen = range(len(temp))
	for i in xlen:
		nomenclature[name[f]] += [temp[i].pop(-1)]
		temp[i].pop(-1)
		for j in range(len(temp[i])):
			if temp[i][j] == "":
				if j > 1:
					mt = True
					for k in range(j+1, len(temp[i])):
						if temp[i][k] != "":
							mt = False
							break
					if mt:
						temp[i][j] = "./"
					else:
						if temp[i][j-1] != temp[i-1][j-1]:
							raise Exception("fichier CSV incorrect :", f, "présence de case vide pour lauquelle la propagation ni horizontale ni verticale n'est possible")
						else:
							temp[i][j] = temp[i-1][j]
				elif j==1:# pas forcement adapté a tout le monde
					temp[i][j] = temp[i-1][j]
				elif i > 0:
					temp[i][j] = temp[i-1][j]
				else:
					raise Exception("fichier CSV incorrect :", f, "présence de case vide dans la 2e ligne (1e donnée) pour laquelle la propagation horizontale n'est pas possible")
	
	ylen = 0
	for i in temp:
		if len(i) > ylen:
			ylen = len(i)
	ylen = range(ylen)
	for i in xlen:
		branch = tree
		last = ""
		for j in ylen:
			if type(branch) != dict:
				continue
			temp[i][j] = temp[i][j].strip()
			if temp[i][j] not in branch:
				branch[temp[i][j]] = {}
			last = temp[i][j]
			branch = branch[last]
	for i in xlen:
		branch = tree
		for j in ylen:
			if temp[i][j] in branch:
				if branch[temp[i][j]] == {}:
					branch[temp[i][j]] = nomenclature[name[f]].pop(0)
				elif type(branch[temp[i][j]]) == dict:
					branch = branch[temp[i][j]]
	def clear(branch):
		if type(branch) == dict:
			if "./" in branch and len(branch) == 1:
				return clear(branch["./"])
			else:
				for i in branch:
					branch[i] = clear(branch[i])
		return branch
	tree = clear(tree)

def any_in(thing, what):
	for i in thing:
		if i in what:
			return True
	return False

sigles = {"xx-xx-202x":"([0-2][0-9]|3[01])-(0[1-9]|1[012])-202[56]",
		  "vX.X": "v[0-9]+\\.[0-9]+",
		  "[Initiales]": '([A-Z][a-zA-Z]{0,2}[A-Z]_)*[A-Z][a-zA-Z]{0,2}[A-Z]',
		  "[Description]": ".+",
		  "LOTX": "LOT(1\\.[1-2]|[2-3])",
		  "RisqueX": "Risque[0-9]+",
		  "FTX" : "FT[0-9]+",
		  "[nom du PIC]": "PI(C|E)(|_.+)",
		  "[Type de l'audit]": "(Ext|Int|Surp)",
		  "RevueX": "Revue[1-4]",
		  "DSX": "DS([1-2]|1\\.[12])",
		  "[Type de réunion]": "(CTFT|RC|RI|interPIC|TP|TQ|RFD)",
		  "DGQX": "DGQ[123]",
		  "soutenanceX" : "soutenance[1-9]+",
		  "[Expérience]": "(pH[12]|UV[12]|Température|Turbulence)"
		} # spécification des sigles et traduction en REGEX 
# https://regex101.com/ pour debug un regex
# [0-9] pour un chiffre, [a-z] pour une lettre minuscule, [A-Z] pour une majuscule, [a-zA-Z] poue une lettre
# (exprA|exprB|exprC) pour une expression au choix, [ab1d] pour un caractère dans la liste 

ignoredfiles = [".keep", ".gitkeep"] #exact filename of files which don't need to be scanned
ignoredfileformat = ['.*\.lnk', '~\$.*'] # file formats which don't need to be scanned (temporary files and shortcuts)
ignoredfolders = [] # name of folders which don't need to be scanned

relpath = "../"
folders = ["Archive", "Versions Actives"]

abspath = "\\".join(os.path.abspath(os.getcwd() + "/" + relpath).split("\\")) + "\\"

def ignore_file(filename):
	for format in ignoredfileformat:
		match = re.fullmatch(re.compile(format),filename)
		if match:
			return True
	return False

def name_match_rule(name, rule):
	for i in sigles:
		if i in rule:
			rule = rule.replace(i, sigles[i])
	rule = rule + "\\..*"
	match = re.fullmatch(re.compile(rule),name)
	if not match:
		print(rule, name)
		return False
	return True


cst = max([len(i) for i in folders])
lastk = []
print("looking for files at", abspath)
for f in folders:
	ok = True
	print(abspath + f, "exist" + " "*(cst-len(f)) + "\tOK" if os.path.isdir(abspath + f) else "doesn't exist" + " "*(cst-len(f)) + "\tKO")
	print("-"*30)
	arbo = {root.replace(relpath + f,'')[1:]:files for root, _, files in os.walk(relpath + f) if not any_in(ignoredfolders, root)}
	for i in arbo:
		branch = tree
		temp = [k.strip() for j in i.split('/') for k in i.split("\\")]
		while '' in temp:
			temp.remove("")
		for j in ignoredfolders:
			if j in temp:
				continue
		lastk = []
		for k in temp:
			if k not in branch:
				print("Erreur, nom de dossier non reconnu : " + k,"le nom du dossier doit se trouver dans la liste suivante : " + str(list(branch.keys())), "l'erreur se trouve dans : " + f + "\\" + "\\".join(lastk),"", sep='\n')
				raise SystemExit
			else:
				branch = branch[k]
				lastk += [k]
			
		if type(branch) == str:
			for file in arbo[i]:
				if file not in ignoredfiles and not ignore_file(file) and not name_match_rule(file,branch):
					print(temp)
					ok = False
		elif "./" in branch:
			for file in arbo[i]:
				if file not in ignoredfiles and not ignore_file(file) and not name_match_rule(file,branch["./"]):
					print(temp)
					ok = False
	if ok:
		print("everything is ok")
		print("\n\n")