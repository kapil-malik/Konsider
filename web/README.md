# Konsider Web Application

This directory is reserved for the React + Vite + TypeScript website deployed independently from
the Python applications. It will access only the live engine API and will not contain scoring,
source-access, or LLM-provider logic.

The planned production host is AWS Amplify Hosting. Runtime configuration should flow through
browser-safe Vite variables such as `VITE_API_BASE_URL`; storage, source, and LLM credentials stay
behind the live engine.

The website begins in Sprint 3. See `docs/components/web-application.md` and `docs/roadmap.md`.
