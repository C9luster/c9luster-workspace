# 横滑容器两侧渐隐

横向滚动列表（卡片、缩略图、标签等）常需要在左右边缘做渐隐，提示「还能继续滑」。

## 场景

```text
┌────────────────────────────────┐
│ ░░  [item] [item] [item] …  ░░ │  ← 两侧渐隐
└────────────────────────────────┘
         ← 横向 overflow-x: auto
```

## 两种常见做法

### A. 给滚动容器本身挂 `mask-image`，再用 JS 按滚动位置开关

```css
.scroller.is-fade-left.is-fade-right {
  -webkit-mask-image: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 0, 0, 0.35) 6%,
    #000 16%,
    #000 84%,
    rgba(0, 0, 0, 0.35) 94%,
    transparent 100%
  );
  mask-image: linear-gradient(/* 同上 */);
}
```

```ts
function syncFade(el: HTMLElement) {
  const {scrollLeft, scrollWidth, clientWidth} = el;
  const max = scrollWidth - clientWidth;
  const overflow = max > 1;
  el.classList.toggle('is-fade-left', overflow && scrollLeft > 1);
  el.classList.toggle('is-fade-right', overflow && scrollLeft < max - 1);
}

el.addEventListener('scroll', () => syncFade(el), {passive: true});
```

**优点**：滚到最左/最右时，对应侧阴影可以关掉，观感更精细。  
**缺点**：每次滑动都读布局、改 class / 切 mask；低端机上更容易卡顿。`mask-image` 切换本身也有合成成本。

### B. 父级相对定位 + 两侧绝对定位覆盖层（推荐默认）

滚动层只负责滚；渐隐是盖在上面的装饰层，**不跟着内容滚走**，也**不拦点击**。

```html
<div class="scroll-wrap">
  <div class="scroller"><!-- 横向内容 --></div>
  <div class="edge edge--left" aria-hidden="true"></div>
  <div class="edge edge--right" aria-hidden="true"></div>
</div>
```

```css
.scroll-wrap {
  position: relative;
  min-width: 0;
}

.scroller {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.edge {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 16%;
  z-index: 1;
  /* 关键：遮罩可点击穿透 */
  pointer-events: none;
}

.edge--left {
  left: 0;
  /* 用父级/页面底色，不要用 mask 里的 #000 */
  background: linear-gradient(
    90deg,
    #fff 0%,
    rgba(255, 255, 255, 0.65) 37.5%,
    transparent 100%
  );
}

.edge--right {
  right: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.65) 62.5%,
    #fff 100%
  );
}
```

**优点**：滚动路径几乎零额外 JS，CSS 更稳，低端机更友好。  
**缺点**：两侧常显；滚到尽头时，对应侧渐隐仍在（性能换精度）。

## 容易搞混：`mask` 的 `#000` ≠ 覆盖层背景

| 写法 | `#000` / 不透明色的含义 |
|------|-------------------------|
| `mask-image` | 黑 = **内容可见**，透明 = **裁掉** |
| 覆盖层 `background` | 不透明色 = **盖住**下面的内容 |

所以：把 `mask-image` 那串 `#000 → transparent` **原样**拷到覆盖层 `background` 上，边缘会变成黑边。  
覆盖层要用 **父容器底色**（例如页面背景 `#fff`）渐隐到透明。

底色可用变量，方便换肤：

```css
.edge {
  --edge-bg: #fff;
}

.edge--left {
  background: linear-gradient(
    90deg,
    var(--edge-bg) 0%,
    transparent 100%
  );
}
```

## 结构注意点

1. **覆盖层挂在滚动容器外面**（父级 `position: relative`），不要放进 `overflow-x: auto` 的子树里，否则会跟着内容一起滚走。
2. **`pointer-events: none`**，否则边缘可点击区域会被挡住。
3. 宽度用 `%` 或固定 `px` 均可；与原先 mask 的边缘停点大致对齐即可。

## 若既要省 JS，又要「靠边才显示」

不必每次重算整段 mask，只做很轻的显隐：

```ts
el.addEventListener(
  'scroll',
  () => {
    const {scrollLeft, scrollWidth, clientWidth} = el;
    const max = scrollWidth - clientWidth;
    leftEdge.hidden = !(max > 1 && scrollLeft > 1);
    rightEdge.hidden = !(max > 1 && scrollLeft < max - 1);
  },
  {passive: true}
);
```

渐变本身仍是纯 CSS；JS 只切换 `hidden` / `opacity`，比改 `mask-image` 便宜。

## 怎么选

| 需求 | 建议 |
|------|------|
| 一般横滑列表 | 方案 B（常显覆盖层） |
| 必须「到头无阴影」且机型偏弱 | B + 轻量显隐 |
| 必须像素级 mask、且滚动不频繁 | 方案 A 也可 |

## 一句话结论

横滑两侧渐隐：优先 **绝对定位覆盖层 + 底色渐变 + `pointer-events: none`**；  
不要把 `mask-image` 的 `#000` 梯度直接当背景；  
只有在需要「按滚动位置开关」时，再加最轻量的 class/`hidden` 切换。
