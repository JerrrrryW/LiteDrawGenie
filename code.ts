// code.ts

// 建议增加UI的高度以容纳新的动态任务列表
figma.showUI(__html__, { width: 800, height: 600, title: "AI Layered Generator" }); // 高度可以根据需要调整

// 这部分代码完全不需要修改。
// 它的职责是监听来自 UI 的 'create-image' 消息，无论这个消息是由哪个按钮触发的。
// 每当它收到包含 imageBytes 的消息，它都会在Figma画布上创建一个新的、独立的矩形图层并填充图像。
// 这完美地支持了我们逐层生成图片的新工作流程。
figma.ui.onmessage = async (msg) => {
  if (msg.type === 'create-image') {
    const imageBytes = msg.imageBytes;

    try {
      const image = figma.createImage(imageBytes);
      const rect = figma.createRectangle();
      
      // 让新图层尺寸与图片尺寸匹配 (假设图片是1024x1024)
      rect.resize(1024, 1024);
      
      // 为矩形填充图片
      rect.fills = [{ type: 'IMAGE', scaleMode: 'FIT', imageHash: image.hash }];

      // 将图层放置在视口中心
      const { x, y } = figma.viewport.center;
      rect.x = x - rect.width / 2;
      rect.y = y - rect.height / 2;
      
      // 添加到页面并选中
      figma.currentPage.appendChild(rect);
      figma.currentPage.selection = [rect];
      figma.viewport.scrollAndZoomIntoView([rect]);

      figma.notify('Layer successfully generated! ✨');

    } catch (error) {
      figma.notify('Error creating image on canvas.', { error: true });
      console.error(error);
    }
  }
};