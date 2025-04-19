<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

# AUTOMATED TRADING JOURNAL

<em></em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the following tools and technologies:</em>

<img src="https://img.shields.io/badge/TOML-9C4121.svg?style=default&logo=TOML&logoColor=white" alt="TOML">
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=default&logo=Docker&logoColor=white" alt="Docker">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/-pandas-05122A?style=flat&logo=pandas&logoColor=white" alt="pandas">
<img src="https://img.shields.io/badge/CSS-663399.svg?style=default&logo=CSS&logoColor=white" alt="CSS">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

The following project aims at automating the process of journaling your trades. A process that, to many of us,
can be excruciating and tiresome enough for some to slowly give up on it.

Thankfully though, there's been a surge of new platforms that have tried to fix this issue but usually come with 1 or 2 major
inconveniences, the main ones being either:

   - They enforce too high of a subscription cost for the features they offer;
   - It heavily lacks user's customization / freedom to query the data that each particular trader needs.

This application, while still being a small and limited version of a bigger idea, tries to provide a free
alternative to journal automation and dashboard customization.

![Daily Trade Recap.png](obsidian/examples/daily/output/Daily%20Trade%20Recap.png)

---

## Features

### Customize your Journal structure & KPI's
by editing the [config.toml](config.toml) to fit your own needs:

### Containerize, schedule and/or locally run your tasks
by running [setup.cmd](setup.cmd) (on Windows) or [setup.sh](setup.sh) (on Linux), which will request you for the
following details:

- an **API_KEY** (linked to your exchange's trading account);
- an **API_SECRET** (linked to your exchange's trading account);
- a **REPORTS_DIR**ectory (eg, your trading journal app folder) to write the reports into.

Which will then generate:

- a **.env** file with your sensitive data and the reports directory;
- a **docker-compose.yml** file with [this](docker-compose.example.yml) structure;
- _optionally_, a **cron job scheduler** to allow you to set the date(s) and time(s) that will trigger the journal pipeline(s).

At this point, you should have your physical directory mounted to the container's **reports/** output folder, so that you can
access the files afterwards. Please ensure the paths under the `volumes` section in the docker-compose.yml are correct.

### Select the timeframe and date of your reports
by updating the `-tf` or `--timeframe` argument to generate either a "**daily**", "**weekly**" or "**monthly**" report, and the
`-dt` or `--start_date` arguments (in "**_YYYY-mm-dd_**" or "**_YYYY-mm_**" format for monthly reports) to choose from which date the
report should start from

---

## Project Structure

```sh
└── AutomatedTradingJournal/
    ├── app.py
    ├── config.ini
    ├── config.toml
    ├── docker-compose.example.yml
    ├── docker-compose.yml
    ├── dockerfile
    ├── example.env
    ├── logs
    ├── obsidian
    │   ├── css
    │   └── examples
    ├── README.md
    ├── requirements.txt
    ├── setup.cmd
    ├── setup.sh
    ├── src
    │   ├── api
    │   ├── config
    │   ├── data
    │   ├── file
    │   ├── journal_pipeline.py
    │   ├── logging
    │   └── utils
    ├── tests
    │   └── src
```

### Project Index

<details open>
	<summary><b><code>automated-trading-journal</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/app.py'>app.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/config.ini'>config.ini</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/config.toml'>config.toml</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/docker-compose.example.yml'>docker-compose.example.yml</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/docker-compose.yml'>docker-compose.yml</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/dockerfile'>dockerfile</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/other.adoc'>other.adoc</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/readme-chatgpt.adoc'>readme-chatgpt.adoc</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/README.adoc'>README.adoc</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/setup.cmd'>setup.cmd</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/setup.sh'>setup.sh</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- src Submodule -->
	<details>
		<summary><b>src</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ src</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\journal_pipeline.py'>journal_pipeline.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
			</table>
			<!-- api Submodule -->
			<details>
				<summary><b>api</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ src.api</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\api\request_handler.py'>request_handler.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- config Submodule -->
			<details>
				<summary><b>config</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ src.config</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\config\config_loader.py'>config_loader.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- file Submodule -->
			<details>
				<summary><b>file</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ src.file</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\file\file_writer.py'>file_writer.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\file\journal_formatter.py'>journal_formatter.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- logging Submodule -->
			<details>
				<summary><b>logging</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ src.logging</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\logging\logger.py'>logger.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- utils Submodule -->
			<details>
				<summary><b>utils</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ src.utils</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\utils\config.py'>config.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\utils\config_vars.py'>config_vars.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\utils\df_vars.py'>df_vars.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\utils\file_vars.py'>file_vars.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\utils\format_vars.py'>format_vars.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\utils\session_vars.py'>session_vars.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/DawnSyndrome/automated-trading-journal\/blob/master/src\utils\utils.py'>utils.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following main dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip
- **Container Runtime:** Docker

### Installation

Build AutomatedTradingJournal from the source and install dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/DawnSyndrome/automated-trading-journal
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd automated-trading-journal
    ```

3. **Ensure you have the latest version of pip:**
    ```sh
    ❯ python -m pip install --upgrade pip
    ```

4. **Install all the project's dependencies:**
    ```sh
    ❯ pip install -r requirements.txt
    ```
   
### Usage

You can run the project in the following ways:

**Locally:**
by running `app.py` through your IDE of choice or through the CLI:
```sh
python app.py --timeframe "{timeframe}" --start_date "{start_date}" # in YYYY-mm-dd or YYYY-mm format
```

**Using [docker](https://www.docker.com/):**
```sh
docker build .
docker run -it {image_name}
```

**Using [docker-compose](https://docs.docker.com/compose/):**
```sh
docker-compose build {service_name}
docker-compose run {service_name}
```

### Testing

automated-trading-journal uses the **pytest** test framework. Run the test suiteand create a test report by:

**Making sure you have _pytest_ and _coverage_ installed:**
```sh
pip install pytest coverage
```

**Run the test report:**
```sh
coverage run -m pytest tests/
```

---

## (Potential) Roadmap

- [ ] **`Additional Exchange Support`**: Extend the app support for other exchanges;
- [ ] **`Additional App Support`**: Allow the app to generate files in other formats / for other apps (eg. Notion, etc).
- [ ] **`Additional KPIs`**: Implement additional trade stats based on users's requests.

---

## Contributing

Feel free to

- 💬 Share your insights, provide feedback, or ask questions.
- 🐛 Submit bugs found or log feature requests for the `automated-trading-journal` project.
- 💡 Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your LOCAL account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/DawnSyndrome/automated-trading-journal
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to LOCAL**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

---


<div align="right">

[![][back-to-top]](#top)

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square
