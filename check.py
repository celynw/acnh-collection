#!/usr/bin/env python3
import argparse
from pathlib import Path
from enum import Enum
from git import Repo
from fuzzywuzzy import fuzz, process
import colorama

from kellog import debug, warning, error

class Status(Enum):
	AVAILABLE = 1
	CHANGED = 2
	FINISHED = 3

class Item():
	def __init__(self, line, status, removed_item=None):
		self.status = status
		self.name = Item.name(line)
		self.cost = Item.cost(line)
		if any([self.status == s for s in [Status.AVAILABLE, Status.FINISHED]]):
			self.variations = line.split("|")[-1].strip().split(", ")
		elif self.status == Status.CHANGED:
			old = removed_item.variations
			new = line.split("|")[-1].strip().split(", ")
			self.variations_missing, self.variations_present = [], []
			for item in old:
				if item not in new:
					self.variations_missing.append(item)
				else:
					self.variations_present.append(item)
		else:
			raise ValueError(f"Incorrect status '{status}'")

	def __str__(self):
		if self.status == Status.AVAILABLE:
			variations = ", ".join(self.variations)
			if variations == "nan":
				return f"{colorama.Fore.GREEN}{self.name}{colorama.Fore.RESET}: {self.cost}"
			else:
				return f"{colorama.Fore.GREEN}{self.name}: {', '.join(self.variations)}{colorama.Fore.RESET}: {self.cost}"
		if self.status == Status.CHANGED:
			return f"{colorama.Fore.YELLOW}{self.name}: {colorama.Fore.RED}{', '.join(self.variations_missing)}, {colorama.Fore.GREEN}{', '.join(self.variations_present)}{colorama.Fore.RESET}: {self.cost}"
		if self.status == Status.FINISHED:
			variations = ", ".join(self.variations)
			if variations == "nan":
				return f"{colorama.Fore.RED}{self.name}{colorama.Fore.RESET}: {self.cost}"
			else:
				return f"{colorama.Fore.RED}{self.name}: {', '.join(self.variations)}{colorama.Fore.RESET}: {self.cost}"

	@staticmethod
	def name(line):
		return line.split("|")[1].strip()

	@staticmethod
	def cost(line):
		return line.split("|")[3].strip()


def main(args):
	repo = Repo(args.repo_dir)
	# assert not repo.bare
	items = []
	files = list(args.repo_dir.glob("*.md"))
	for file in files:
		diff = repo.git.diff(repo.commit("start"), None, file.relative_to(args.repo_dir))
		for line in diff.split("\n"):
			if any([line.startswith(s) for s in ["+++", "---"]]):
				pass
			elif line.startswith("-"):
				try:
					items.append(Item(line, Status.FINISHED))
				except Exception:
					pass
			elif line.strip().startswith("| "):
				try:
					items.append(Item(line, Status.AVAILABLE))
				except Exception:
					pass
			elif line.startswith("+"):
				name = Item.name(line)
				for i, item in enumerate(items):
					if item.status == Status.FINISHED and item.name == name:
						removed = i
						break
				items.append(Item(line, Status.CHANGED, items.pop(i)))

	# Only want to compare item name, not the variation name
	idxed = [(idx, el.name) for idx, el in enumerate(items)]
	matches = process.extract(args.search_term, idxed, limit=5, scorer=fuzz.partial_token_sort_ratio)
	for result, score in matches:
		match = items[result[0]]
		print(match)


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("repo_dir", type=str, help="Where the markdown repository is stored")
	parser.add_argument("search_term", type=str, nargs="*", help="Where the markdown repository is stored")

	args = parser.parse_args()
	args.repo_dir = Path(args.repo_dir)
	args.search_term = " ".join(args.search_term)

	return args


if __name__ == "__main__":
	main(parse_args())
