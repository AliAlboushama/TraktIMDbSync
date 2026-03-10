# ⚡ Quick Start Guide

Get up and running with TraktIMDbSync in 5 minutes!

---

## 📦 1. Install

```bash
pip install TraktIMDbSync
```

---

## 🔑 2. Get Trakt API Credentials

1. Go to [trakt.tv/oauth/applications](https://trakt.tv/oauth/applications)
2. Click **"New Application"**
3. Fill in:
   - **Name**: `TraktIMDbSync`
   - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob`
4. Click **"Save App"**
5. Copy your **Client ID** and **Client Secret**

---

## 🚀 3. Run First Sync

```bash
python -m TraktIMDbSync
```

You'll be prompted for:
- ✅ Trakt Client ID
- ✅ Trakt Client Secret  
- ✅ Trakt Authorization Code (you'll get a URL to visit)
- ✅ IMDB Email/Phone
- ✅ IMDB Password
- ✅ Sync preferences

---

## 🎯 4. Choose What to Sync

When asked, select your preferences:

```
Do you want to sync watchlists? (y/n): y
Do you want to sync ratings? (y/n): y
Do you want to remove watched items from watchlists? (y/n): n
Do you want to sync reviews? (y/n): n
Do you want to sync your watch history? (y/n): y
Do you want to mark rated movies and episodes as watched? (y/n): n
Do you want to remove watchlist items older than x days? (y/n): n
```

**Recommended for first-time users:**
- ✅ Sync watchlists
- ✅ Sync ratings
- ✅ Sync watch history
- ❌ Everything else (you can enable later)

---

## ⏱️ 5. Wait for Sync

The syncer will:

1. **Fetch Trakt data** (~20-60 seconds)
2. **Generate IMDB exports** (~2-5 minutes)
3. **Download & parse** (~30 seconds)
4. **Analyze differences** (~1-5 seconds)
5. **Sync data** (varies based on quantity)

Total time: **5-15 minutes** for first sync (1000-5000 items)

---

## ✅ 6. Verify Results

Check your accounts:
- 🎬 [IMDB Watchlist](https://www.imdb.com/list/watchlist)
- ⭐ [IMDB Ratings](https://www.imdb.com/list/ratings)
- 🎥 [IMDB Check-ins](https://www.imdb.com/list/checkins)
- 📝 [Trakt Profile](https://trakt.tv/users/me)

---

## 🔄 7. Run Regular Syncs

```bash
# Just run again - it remembers your settings!
python -m TraktIMDbSync
```

Subsequent syncs are much faster (only syncs new items).

---

## 💡 Pro Tips

### Speed Up Syncs
- Only sync what you need
- Run syncs regularly (less to sync each time)
- Close other browser windows during sync

### Troubleshooting
- **Stuck on IMDB exports?** Normal for 1000+ items, wait up to 20 minutes
- **Login failed?** Check your IMDB credentials
- **Trakt error?** Verify your API credentials
- **Something broken?** Check `log.txt` in your package directory

### Advanced Options

```bash
# Clear your saved credentials
python -m TraktIMDbSync --clear-user-data

# Clear browser cache
python -m TraktIMDbSync --clear-cache

# Find log file location
python -m TraktIMDbSync --directory
```

---

## 🎓 Next Steps

- 📖 Read the [Full README](README.md) for all features
- 🔧 Learn about [Advanced Configuration](README.md#️-configuration)
- 🐛 Check [Troubleshooting](README.md#-troubleshooting) if you have issues
- ⚡ See [Performance Tips](README.md#-performance-improvements)

---

## ❓ Need Help?

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/AliAlboushama/TraktIMDbSync/issues)
- 💬 [Ask Questions](https://github.com/AliAlboushama/TraktIMDbSync/discussions)

---

<div align="center">

**That's it! You're syncing! 🎉**

[⬆ Back to README](README.md)

</div>


