# de-co-dev.github.io

Public legal documents (Terms and Conditions, Privacy Policy) of de-co-dev's
projects, published with GitHub Pages at https://de-co-dev.github.io/.

## Structure

```
<project>/
├── textos/            source texts (edit these)
│   ├── terms-es.md
│   ├── terms-en.md
│   ├── privacy-es.md
│   └── privacy-en.md
├── es/terminos.html   generated
├── es/privacidad.html generated
├── en/terms.html      generated
├── en/privacy.html    generated
└── index.html         generated
```

## Editing a text

1. Edit the `.md` file in `<project>/textos/`.
2. Run `python3 build.py`.
3. Commit the `.md` and the generated `.html`, then push. GitHub Pages
   publishes it in a minute or two.

For Pill Reminder, a changed text must also be published as a new version in
its Supabase `legal_documents` table (`publish_legal_document()`): the app
asks users to accept the version stored there, and that copy is the legal
record of what each user accepted.

## Adding a project

Create `<project>/textos/` with the four `.md` files, add the project to
`PROJECTS` in `build.py`, run it, commit and push.

## Projects

- **Pill Reminder**: https://de-co-dev.github.io/pillreminder/
