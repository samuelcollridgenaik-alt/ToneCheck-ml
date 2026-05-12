# GitHub Publishing Guide

## What I Need To Publish For You

To publish this repo for you from this environment, I need:

1. a GitHub repository name
2. GitHub authentication available in the shell environment

Example repository name:

```text
samuelcollridgenaik/tonecheck-ml
```

## Safest Way To Give Me GitHub Access

Do not paste the token into chat.

Instead, set it in your terminal before asking me to publish:

```bash
export GITHUB_TOKEN=your_token_here
```

Then tell me:

```text
ready: samuelcollridgenaik/tonecheck-ml
```

## Recommended Token Types

### Simplest option

Use a classic personal access token with:

- `repo` scope for private repos
- `public_repo` scope for public-only publishing

GitHub’s docs say personal access tokens can be used in place of a password for HTTPS Git operations, and the repository REST docs say classic tokens need `public_repo` or `repo` to create a public repository, and `repo` for a private repository.  
Sources:

- [Managing personal access tokens](https://docs.github.com/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Repositories REST API](https://docs.github.com/en/rest/repos/repos)

### Fine-grained token option

If you prefer a fine-grained personal access token, the safest practical setup is:

- repository `Contents`: `Read and write`
- repository `Metadata`: `Read`
- repository `Administration`: `Write` if you want me to create the repository for you

GitHub’s fine-grained permission docs list repository administration as required for repository creation endpoints, and repository metadata/contents permissions for normal repository access patterns.  
Sources:

- [Fine-grained token permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens?apiVersion=latest)
- [Repositories REST API](https://docs.github.com/en/rest/repos/repos)

## What I Can Do Once Access Is Present

Once the token is available, I can:

1. create the GitHub repository if needed
2. add the git remote
3. commit the project cleanly
4. push the branch
5. help with deployment immediately after

## Optional: Existing Repository

If you already created the GitHub repository yourself, send me the HTTPS remote URL instead, for example:

```text
https://github.com/samuelcollridgenaik/tonecheck-ml.git
```

Then I only need push access, not repo-creation access.
