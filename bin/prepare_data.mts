#!/usr/bin/env npx -S tsx
import 'zx/globals';

const pblue = (s: string) => console.log(chalk.blue(s));

pblue("downloading git repo ...")
await $`git clone https://github.com/google-research-datasets/eth_py150_open.git --depth 1`
