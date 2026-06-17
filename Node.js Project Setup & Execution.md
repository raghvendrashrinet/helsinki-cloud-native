# Node.js Project Setup & Execution Guide

This guide explains the standard workflow for setting up and running a Node.js application, detailing how `npm` interacts with your project files.

## Overview

Node.js projects rely on two main configuration areas within the `package.json` file:
1.  **Dependencies**: Libraries required for the code to run.
2.  **Scripts**: Custom commands to start, test, or build the application.

---

## 1. Installation Phase (`npm install`)

Before running the application, you must install the required libraries.

### The Command
```bash
npm install
```
- reads the dependencies
-  It creates a `node_modules` directory containing all the code for those packages.
-  Locking: It generates or updates `package-lock.json` to ensure exact version consistency across different environments.
---
# Node.js Execution Phase Guide

This document details how to run, manage, and debug Node.js applications using the `npm run` command and direct execution.

## 1. The Core Concept

The execution phase relies entirely on the **`scripts`** object within your `package.json` file. `npm` acts as a task runner, executing shell commands defined in this configuration.

### How `npm run` Works
1.  **Locate**: Finds `package.json` in the current working directory.
2.  **Parse**: Reads the `"scripts"` section.
3.  **Match**: Looks for the key matching your command (e.g., `start`, `dev`, `build`).
4.  **Execute**: Runs the associated shell command in a sub-shell.

---

## 2. Standard Execution Commands

### A. Running Defined Scripts
Use this for any custom command defined in `package.json`.

```bash
npm run <script-name>
```

#### package.json
```json
{
  "name": "my-web-server",
  "version": "1.0.0",
  "description": "A simple Node.js web server",
  "main": "app.js",
  
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  },

  "dependencies": {
    "express": "^4.18.2"
  },
  
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

### Step A: a Simple Server (`app.js`)
---
First, create a file named `app.js` with this basic server code:

```javascript
// app.js
const http = require('http');

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello World! Server is running.\n');
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
```

### Step B: Initialize and Configure package.json
Run `npm init -y `to generate a default file, then edit it to add scripts. Your `package.json` should look like this:
```json
{
  "name": "my-execution-demo",
  "version": "1.0.0",
  "description": "Demo for npm run execution",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "echo \"Running tests...\" && exit 0"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
```

### Step C: Install Dependencies (if using nodemon)
If you want to use the dev script, install nodemon:
```bash
npm install --save-dev nodemon
```

### Step D: Execute the Application
Now you can run the scripts defined above:
```bash
# Run the production server
npm start

# OR run the development server with auto-restart
npm run dev
```
### Advanced Execution Techniques
You can pass arguments to your Node.js script by adding them after --.
```
npm start -- --port=3005 --debug
```
Result : `node app.js --port=3005 --debug`


