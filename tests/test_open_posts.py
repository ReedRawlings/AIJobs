import os
import csv
import glob
from datetime import date
import unittest


SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "snapshots")


def load_snapshot_for_date(target_date: date):
    date_str = target_date.isoformat()
    candidate = os.path.join(SNAPSHOT_DIR, f"{date_str}.csv")
    if os.path.exists(candidate):
        return candidate

    # Fallback: latest snapshot in directory
    snapshots = sorted(glob.glob(os.path.join(SNAPSHOT_DIR, "*.csv")))
    return snapshots[-1] if snapshots else None


def read_jobs_from_snapshot(snapshot_path: str):
    jobs = []
    with open(snapshot_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(row)
    return jobs


class TestOpenCareerPosts(unittest.TestCase):
    def test_list_open_posts_today(self):
        snapshot_path = load_snapshot_for_date(date.today())
        self.assertIsNotNone(snapshot_path, "No snapshot CSV found to validate")

        jobs = read_jobs_from_snapshot(snapshot_path)
        self.assertGreater(len(jobs), 0, "Snapshot contains no jobs")

        # Open posts: anything not closed
        open_jobs = [j for j in jobs if (j.get("status") or "").lower() != "closed"]

        # Basic sanity: open should be at least one when sample data exists
        self.assertGreater(len(open_jobs), 0, "No open jobs found in today's snapshot")

        # Print a compact review line for each open post to test output
        for j in open_jobs:
            print(f"{j.get('company_name')} | {j.get('title')} | {j.get('location')} | {j.get('job_url')}")


if __name__ == "__main__":
    unittest.main()


