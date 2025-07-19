// code.ts

// 增加了UI的高度以容纳新的文本框
figma.showUI(__html__, { width: 340, height: 800, title: "AI Image Enhancer & Generator" });

// 这部分代码完全不需要修改，因为它只负责接收和处理最终的图片数据
figma.ui.onmessage = async (msg) => {
  if (msg.type === 'create-image') {
    const imageBytes = msg.imageBytes;

    try {
      // 1. 使用图片数据创建一个 Figma Image Fill
      const image = figma.createImage(imageBytes);

      // 2. 创建一个矩形节点
      const rect = figma.createRectangle();
      // Gemini 图片通常是 1024x1024，我们以此尺寸创建矩形
      rect.resize(1024, 1024);

      // 3. 将图片填充到矩形中
      rect.fills = [{ type: 'IMAGE', scaleMode: 'FIT', imageHash: image.hash }];

      // 4. 将矩形放置在视口中央
      const { x, y } = figma.viewport.center;
      rect.x = x - rect.width / 2;
      rect.y = y - rect.height / 2;
      
      // 5. 将新创建的图层添加到当前页面并选中
      figma.currentPage.appendChild(rect);
      figma.currentPage.selection = [rect];
      figma.viewport.scrollAndZoomIntoView([rect]);

      // 6. not close plugin, but show a success message
      figma.notify('Image successfully generated! ✨');

    } catch (error) {
      figma.notify('Error creating image on canvas.');
      console.error(error);
    }
  }
};