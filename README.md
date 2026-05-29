# Dimension Hatred site

Static site for the Dimension Hatred fan mod.

## Structure

- `index.html` : public homepage with announcements.
- `admin/index.html` : hidden admin dashboard for publishing announcements.

## Announcements

- Public announcements are read from Firestore.
- The hidden admin page uses Firebase Auth to sign in.
- When publishing, the admin enters a pseudo that is stored as the announcement author.

## Local preview

Serve the folder locally and open the homepage.

Example:

```bash
python -m http.server 8000
```

Then open `http://127.0.0.1:8000/`.
