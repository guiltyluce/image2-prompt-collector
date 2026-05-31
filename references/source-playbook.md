# Public Source Playbook

## Source Priority

Prefer sources where prompts and images are intentionally shared for reuse or learning:

1. GitHub repositories and awesome lists about GPT Image / image-generation prompts.
2. Public Reddit posts where prompts are included.
3. Public X/Twitter posts where prompts are included.
4. Public 小红书 posts where prompts are included and visible through the logged-in browser.
5. Public blog posts, newsletters, or docs with prompt examples.

## Collection Rules

- Keep source URL and visible creator/source label.
- Capture only prompt-level data, short title, image, and attribution.
- Do not copy long article bodies.
- Do not use private chats, private groups, paywalled content, or content behind non-user-approved access.
- Prefer candidates with clear reusable structure over novelty-only memes.

## Quality Gate

Accept candidates that have:

- A complete prompt, not just a vague idea.
- A visible generated example image or a prompt that can be generated now.
- Reusable structure: placeholders, style recipe, composition recipe, visual constraints, or clear domain utility.
- No obvious unsafe, hateful, sexual, or privacy-invasive content.
- No request to imitate a living private person or create deceptive real-person media.

Reject or defer candidates that:

- Have no prompt.
- Have an image but only a one-line vague caption.
- Are too dependent on a private uploaded reference image that is unavailable.
- Require unclear copyrighted character/IP usage as the core value.
- Need image generation but generation is unavailable in the current run.

## Platform Notes

### GitHub

Use repo READMEs, docs, data files, and image folders. Prefer structured markdown or JSON. If cloning public repos, keep them under the workspace.

### Reddit

Use public posts and comments with prompt text. Store Reddit URL and subreddit/post title. Quote minimally; paraphrase notes.

### X/Twitter

Use public posts. If the browser is logged in, collect visible prompt text and images. Store post URL and handle. Do not bypass access restrictions.

### 小红书

Use only public-visible posts. Since web pages can be dynamic, use the logged-in browser if available. Store the post URL or visible note identifier plus creator label.

## Candidate Normalization

For each candidate, produce:

- `title`: short Chinese title, max 40 chars if possible.
- `prompt`: full usable prompt.
- `image_path`: local downloaded/generated image path.
- `source_platform`: one of the allowed platform labels.
- `source`: handle/title.
- `source_url`: public URL.
- `style_tag`: mapped to a Base category.
- `usage_note`: how to adapt the prompt.

Then import with `scripts/import_candidates.py`.
