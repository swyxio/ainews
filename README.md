# Hacker News of AI

Project currently deployed at: https://ainewsdev-production.up.railway.app

Code hosted at: https://github.com/swyxio/ainews

## dev

enter virtual env, install requirements then

```bash
python main.py
open http://localhost:5001
```

## deploy instructions

```bash
fh_railway_deploy ainews_dev
```

theres a bug in the deploy script right now, our workarounds are here: https://github.com/AnswerDotAI/fasthtml/issues/186


## misc info

- source code bootstrapped from https://github.com/AnswerDotAI/fasthtml/blob/main/examples/adv_app.py
- https://h2x.answer.ai/ is a tool that can convert HTML to FT (fastcore.xml) and back, which is useful for getting a quick starting point when you have an HTML example to start from.