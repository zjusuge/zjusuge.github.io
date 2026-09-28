# 学术主页维护说明

页面采用原仓库的 Jekyll / GitHub Pages 架构，不需要数据库或后台。论文、基金和代码项目集中在 `_data` 中，主页和英文 CV 共用同一份记录。

## 最常用的四个文件

| 要改什么 | 编辑文件 |
|---|---|
| 新论文、DOI、作者、年份 | `_data/publications.yml` |
| 外审手稿、作者、投稿状态 | `_data/manuscripts.yml` |
| 新基金、个人资助、合作项目 | `_data/funding.yml` |
| 新 GitHub 项目 | `_data/software.yml` |
| 博后求职开关、毕业时间、邮箱 | `_data/profile.yml` |

在 GitHub 中打开对应文件，点击铅笔图标，复制一个现有条目后修改。建议选择创建分支并提交 Pull Request；`Check academic homepage` 会检查数据及构建。合并后由仓库原有 GitHub Pages 发布机制更新网站。

## 增加论文

将新条目放在对应年份处，保持年份从新到旧。`id` 必须唯一；同一篇文章接受、在线发表和正式出版时更新原条目，避免重复添加。

```yaml
- id: paper-your-short-title
  year: 2027
  title: "Exact published article title"
  authors: "Tianlong Wang, J. Chu, H. Sun*"
  venue: "Journal name, volume, pages or article number."
  type: Journal article
  topic: Debris flows
  links:
    - label: DOI
      url: https://doi.org/10.xxxx/your-real-doi
    - label: Code
      url: https://github.com/zjusuge/your-repository
```

这是格式示例，请替换 DOI 和仓库地址后再提交。没有公开链接时写 `links: []`，删除示例的 `links` 列表。

- `authors` 是普通文字；名字写为 `Tianlong Wang` 会自动加粗，`*` 会显示为通讯作者标记。只按论文原文标记作者身份。
- `topic` 可选 `Debris flows`、`Hydrology`、`Geotechnics`、`Algorithms`；会议论文的 `type` 为 `Conference paper`。
- 外审手稿放在 `_data/manuscripts.yml`，主页展开列表和 CV 共用。`status` 用 `Under review` 或 `Under review following revision`，`status_as_of` 保存作者记录日期（YYYY-MM-DD）。不要将外审文章列为已发表。文章发表后移至 `publications.yml` 并删除原手稿记录，避免重复。
- `_data/home.yml` 的 `ongoing` 只维护研究方向摘要；不是投稿状态清单。准备中的工作不写成外审。
- CV 研究简介、可入职日期、更新时间维护在 `_data/profile.yml` 的 `research_profile`、`available_from`、`cv_updated`。内容更新后使用 `/cv/` 的 Print / Save as PDF 重新导出并检查分页，旧 PDF 不会自动更新。
- 要更换三篇代表作，修改 `_data/home.yml` 的 `selected`。`paper_id` 必须对应论文的 `id`；同时更新代表作标题、年份和期刊说明。
- 代表作目前采用纯文字卡片，不展示论文原图。学术主页顶部 `Poetry` 链接进入诗歌站，诗歌站顶部 `学术主页` 链接返回。
- 教育与导师链接在 `_data/education.yml`，`supervisor_url` 为学校个人主页。主页与 CV 共用数据，目前只展示浙大博士和 NTU 联培经历。
- 审稿期刊在 `_data/service.yml` 的 `reviewing` 中新增一行，主页与 CV 会同步更新。
- 诗歌网站位于 `/poetry/`；作品维护见 [诗歌网站维护说明](POETRY-zh.md)。
- 不需要复制论文 PDF 到网站。使用 DOI 链接即可；只有确认可公开分享的版本才添加 PDF 链接。

## 增加基金或项目

```yaml
- category: individual
  period: "2027–2029"
  title: "Official programme name"
  funder: "Funding organisation"
  role: PI
  project: "Research project title"
  details: "Grant No. XXXXX · Funding: RMB XXXXX."
```

`category` 为 `individual` 或 `collaborative`。个人主持项目可写 `PI`，奖学金写 `Recipient`，作为核心参与成员写 `Core team member`。合作项目金额须明确是项目总经费，不能写成个人获得的经费。

## 增加 GitHub 项目

```yaml
- name: YourProject
  category: Catchment forecasting
  description: "One sentence describing what users can do with the code."
  tags: [Hydrology, Forecasting]
  links:
    - label: Repository
      url: https://github.com/zjusuge/your-repository
```

## 结束博后求职

在 `_data/profile.yml` 中设置 `seeking_postdoc: false`，顶部招聘提示与 CV 求职提示会隐藏。联系区仍可用于学术交流。主页联系按钮会同步切换为学术合作入口；页面的研究经历不会自动变化。

## 其他内容

- `_data/home.yml`：研究方向、代表工作和当前稿件研究；科研主线不是论文数量统计。
- `_data/education.yml`：教育信息，同时用于主页和 CV。
- `_data/service.yml`：英文 CV 的期刊审稿及学会会员。
- `_pages/about.html`：版式及较少变动的荣誉、专利、其他经历。
- `_pages/cv.html`：英文研究 CV，使用浏览器打印或“保存为 PDF”。
- `assets/css/editorial.css`：新版配色、字号、布局。`--ink` 深蓝，`--teal` 青绿，`--clay` 赭色，`--paper` 暖白。
- `images/portrait-academic.jpeg`：从本人中文简历提取的原始证件照。需要换照片时替换该文件或修改图片路径。

## 检查与预览

```sh
python -m pip install PyYAML==6.0.3
python scripts/validate_content.py
bundle install
bundle exec jekyll serve
```

浏览器打开本地 Jekyll 地址。修改 `_config.yml` 后须重启服务。构建检查会发现 YAML 格式、重复 DOI、重复 ID、失效的代表作引用、缺失的内部文件和未渲染模板。

所有论文、基金和项目在构建时生成 HTML，关闭 JavaScript 仍能阅读。JavaScript 仅增强搜索、移动菜单、跳转与打印。外部字体不可用时使用系统字体，不影响主要内容。

## 发布前仍需本人核对的履历细节

- 优秀博士论文资助 825011A：中文 CV 与旧主页的起止月份和结题状态不一致，新版仅保留一致的 2025–2026 年与金额。
- SWAT-ML-SHAP 作者身份：按提供的论文 PDF，孙红月为通讯作者；未沿用中文 CV 给王天龙加星的写法。
- 当前稿件只标记为 `Current research / Manuscripts`，未推断其最新投稿或录用状态。
- 其他早期论文的作者顺序保留既有主页记录，未做全部出版商元数据的独立核验。正式投递前可逐篇进一步核对。
