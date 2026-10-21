# Contributing

Thanks for helping. Issues and documentation fixes are welcome; contributions are accepted under the licences described below.

## Ground rules

1. **No sensitive data, ever.** No secrets, no customer or client data, no personal
   data, not even in examples. Use synthetic fixtures.
2. **Open an issue first** for anything larger than a typo, so we agree on the shape.
3. **Small pull requests.** One change per PR, with a clear description and a check
   you ran.
4. **Sign off your commits** under the [Developer Certificate of Origin](https://developercertificate.org/):
   `git commit -s`. This certifies you wrote the change and may contribute it.
5. **AI-assisted contributions are welcome**, provided you have reviewed and tested
   what you submit and can explain it.

## Development

Run `bash scripts/check.sh` before opening a pull request. Maintainers also run it with `DENY_LIST` set to a private list of client terms before every release. CI runs the same script:
a full-history secret scan, a link check and any project tests.

## Licensing of contributions

Code contributions are accepted under Apache-2.0 (inbound = outbound). By contributing documentation you license it to the author under CC BY 4.0, so it can be included in the CC BY-NC-ND 4.0 documentation.
