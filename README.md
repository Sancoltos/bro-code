# bro-code

A CLI tool that lets you chat with Claude from your terminal.

## Requirements

- Python 3.10+
- An Anthropic API key (get one at https://console.anthropic.com/settings/keys)

## Installation

Clone the repo and install:

```
git clone https://github.com/Sancoltos/bro-code.git
cd bro-code
pip install -e .
```

## Set your API key

**Windows:**
```
setx ANTHROPIC_API_KEY "your-key-here"
```
Then restart your terminal.

**Mac/Linux:**
```
export ANTHROPIC_API_KEY="your-key-here"
```
To make it permanent, add that line to your `~/.bashrc` or `~/.zshrc`.

## Run

```
bro
```

Type your question or task and press Enter. When Claude wants to read, write, or run something on your machine it will ask for your approval before doing anything.

Type `exit` or `quit` to stop.
