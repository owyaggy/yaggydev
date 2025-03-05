# Ensuring Automatic Deployment Works

## Deploying `staging` branch to working server

```sh
git checkout staging
git push deploy staging
```

## Merging `staging` branch into `main` branch

```sh
git checkout main
git merge staging
git push origin main
```

## Deploying new `main` branch

```sh
git push deploy main
```

Alternatively, use **Pull Requests**.