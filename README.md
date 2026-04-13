# bro-code

A CLI tool that lets you chat with Claude from your terminal.

## Requirements

- Python 3.10+
- An Anthropic API key (get one at https://console.anthropic.com/settings/keys)

## Installation

Clone the repo:

```
git clone https://github.com/Sancoltos/bro-code.git
cd bro-code
```

Run first-time setup:

```
python setup.py first_setup
```

This will install dependencies, fix your PATH on Windows, and walk you through saving your API key.

## Run

Open a new terminal, then:

```
bro
```

Type your question or task and press Enter. When Claude wants to read, write, or run something on your machine it will ask for your approval before doing anything.

Type `exit` or `quit` to stop.

## Update your API key later

```
python setup.py configure_anthropic
```
