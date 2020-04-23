#!/usr/bin/env python3
import argparse
from pathlib import Path
from tqdm import tqdm
import ujson
import pandas as pd

from kellog import debug

def main(args):
	db = None
	paths = list((Path(__file__).resolve().parent.parent.parent / "villagerdb/data/items/").glob("*.json"))
	for path in tqdm(paths):
		with open(path, "r") as file:
			json = ujson.load(file)

		df = pd.DataFrame(json)
		try:
			df = df.loc["nh"]
		except KeyError:
			continue
		df.name = None

		try:
			df["games"]["sellPrice"] = f'{df["games"]["sellPrice"]["value"]} {df["games"]["sellPrice"]["currency"]}'
		except KeyError:
			pass
		try:
			df["games"]["buyPrices"] = ", ".join([f'{p["value"]} {p["currency"]}' for p in df["games"]["buyPrices"]])
		except KeyError:
			pass
		try:
			df["games"]["variations"] = ", ".join(list(df["games"]["variations"].keys()))
		except KeyError:
			pass
		try:
			df["games"]["recipe"] = ", ".join([f'{k} {v}' for k, v in df["games"]["recipe"].items()])
		except KeyError:
			pass

		df = pd.concat([df.drop(["games"]), pd.Series(df["games"]).to_frame()])

		if db is None:
			db = pd.DataFrame(df)
		else:
			db = pd.concat([db, df], axis=1)

	db = db.transpose()
	db = db.sort_values("category") # Not strictly necessary
	db = db.drop("id", axis=1)
	db = db.reset_index(drop=True)

	debug(f"\n{db}")

	for cat in db.category.unique():
		category = db.loc[db["category"] == cat]
		category = category.drop(["category"], axis=1)
		with open(args.out_dir / f"{cat}.md", "w") as file:
			file.write(category.to_markdown(showindex=False))
			file.write("\n")


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-o", "--out-dir", help="Place to store markdown output")

	args = parser.parse_args()
	if args.out_dir is not None:
		args.out_dir = Path(args.out_dir)
	args.out_dir.mkdir(exist_ok=True)

	return args


if __name__ == "__main__":
	main(parse_args())
