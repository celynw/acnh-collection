#!/usr/bin/env python3
import argparse
from pathlib import Path
from git import Repo, Blob

from kellog import debug, info, warning

def main(args):
	repo = Repo(args.repo_dir)
	unmerged_blobs = repo.index.unmerged_blobs()
	for path, blobs in unmerged_blobs.items():
		# Blobs:
		# - Original?
		# - Current
		# - Incoming
		blobs = [(blob[1].data_stream.read()).decode().replace("\\n", "\n") for blob in blobs[1:]]

		currentItems = {}
		for line in blobs[0].split("\n")[2:-1]:
			item = [l.strip() for l in line.split("|")]
			currentItems[item[1]] = item[-1] # Name: variations

		incomingItems = []
		for line in blobs[1].split("\n")[2:-1]:
			incomingItems.append(line.strip())

		keep = []
		for item in incomingItems:
			name = item.split("|")[1].strip()
			variations = item.split("|")[-1].strip()
			if name in currentItems.keys():
				if variations != currentItems[name]:
					debug(variations)
					warning(currentItems[name])
				keep.append(item.rsplit("|", 1)[0] + f"| {currentItems[name]}")

		with open(args.repo_dir / path, "w") as file:
			file.write("\n".join(blobs[1].split("\n")[:2] + keep) + "\n")


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("repo_dir", help="Location to store markdown output")

	args = parser.parse_args()
	if args.repo_dir is not None:
		args.repo_dir = Path(args.repo_dir)

	return args


if __name__ == "__main__":
	main(parse_args())
