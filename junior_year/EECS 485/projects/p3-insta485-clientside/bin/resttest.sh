#!/bin/bash
set -Eeuo pipefail
set -x

http \
	--session=./session.json \
	--form POST \
	"http://localhost:8000/accounts/" \
	username=awdeorio \
	password=password \
	operation=login \

http \
	--session=./session.json \
	"http://localhost:8000/accounts/" \
