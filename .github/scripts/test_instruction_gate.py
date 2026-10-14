import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from instruction_gate import check  # noqa: E402

GOOD = """## Owner instruction (verbatim quote)
> Cut the arm piece out with Smart Cut in the same project.

## Method the owner specified
Smart Cut in the existing project file

## Method actually used
Smart Cut in the existing project file

## Deviations (none / list, each with owner approval link)
none

## Proof (paths to files, frames, test output)
- `renders/arm_cut.png`

## Self-check: I verified the result against the literal instruction
- [x] I re-read the verbatim instruction and the result matches it.
"""

BAD = GOOD.replace("Smart Cut in the existing project file\n\n## Deviations",
                   "Rectangular crop of the frame\n\n## Deviations")


class Gate(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_passing_body(self):
        self.assertEqual(check(GOOD, ["renders/arm_cut.png"], self.d), [])

    def test_failing_body_substituted_method(self):
        errs = check(BAD, ["renders/arm_cut.png"], self.d)
        self.assertTrue(any("differs" in e for e in errs), errs)

    def test_missing_section(self):
        body = GOOD.split("## Proof")[0]
        self.assertTrue(any("Missing required section" in e for e in check(body, [], self.d)))

    def test_empty_section(self):
        body = GOOD.replace("Smart Cut in the existing project file\n\n## Method actually",
                            "\n## Method actually")
        self.assertTrue(any("empty" in e for e in check(body, ["renders/arm_cut.png"], self.d)))

    def test_deviation_without_approval(self):
        body = BAD.replace("none\n", "- used a crop because it was faster\n")
        errs = check(body, ["renders/arm_cut.png"], self.d)
        self.assertTrue(any("approval" in e for e in errs), errs)

    def test_deviation_with_approval_passes(self):
        body = BAD.replace("none\n", "- crop instead of Smart Cut, approved https://github.com/o/r/pull/1#issuecomment-1\n")
        self.assertEqual(check(body, ["renders/arm_cut.png"], self.d), [])

    def test_missing_proof_path(self):
        errs = check(GOOD, [], self.d)
        self.assertTrue(any("Proof path" in e for e in errs), errs)

    def test_proof_path_in_repo(self):
        os.makedirs(os.path.join(self.d, "renders"))
        open(os.path.join(self.d, "renders/arm_cut.png"), "w").close()
        self.assertEqual(check(GOOD, [], self.d), [])

    def test_unticked_selfcheck(self):
        errs = check(GOOD.replace("[x]", "[ ]"), ["renders/arm_cut.png"], self.d)
        self.assertTrue(any("Self-check" in e for e in errs), errs)

    def test_docs_only_exempt(self):
        self.assertEqual(check("", ["README.md", "docs/a.md"], self.d, ["docs-only"]), [])

    def test_docs_only_with_code_fails(self):
        self.assertTrue(check("", ["README.md", "main.py"], self.d, ["docs-only"]))

    def test_dependabot_exempt(self):
        self.assertEqual(check("", ["package.json"], self.d, [], "dependabot[bot]"), [])


if __name__ == "__main__":
    unittest.main()
