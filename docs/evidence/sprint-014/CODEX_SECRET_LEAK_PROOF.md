# Codex secret-leak proof

The Codex health command discards stdin, stdout, and stderr. Tests simulate
secret-looking output and verify it does not enter `health` or
`last_test_result`. The relationship migration stores only provider identity
and authentication mode; Codex's credential binding remains empty.

Public provider projections and the administration list omit configuration and
credential bindings. No credential value, token, account detail, or replayable
CLI output is present in this evidence.
