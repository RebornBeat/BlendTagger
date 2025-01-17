# **BlendTagger**: AI Annotation Tool for 3D Model Training in Blender

**BlendTagger** is an open-source plugin for Blender that allows users to contribute to AI model training by annotating 3D models. This tool provides an intuitive interface for labeling, tagging, and marking 3D objects, meshes, and scenes within Blender. It's designed to facilitate the collection of annotated data to train AI models for tasks like 3D object recognition, generation, and more.

By using **BlendTagger**, Blender users can easily contribute their 3D creation data to AI training efforts, helping build better, more capable generative models for the 3D world.

---

## **Features**

- **3D Object Annotation**: Annotate meshes, vertices, and objects in Blender scenes.
- **Tagging System**: Add custom tags to objects and meshes for classification tasks.
- **AI Model Data Preparation**: Export annotations in popular formats (JSON, CSV, etc.) for AI model training.
- **User-Friendly Interface**: Simple and intuitive toolset integrated directly within Blender.
- **Open-Source**: Free to use, contribute, and modify.
- **Collaboration-Friendly**: Easily share annotated datasets with other users or AI researchers.

---

## **Installation**

### **Pre-requisites**

- Blender 2.9x or newer
- Python 3.7+ (Bundled with Blender)
  
### **Steps**

1. **Download the Plugin**
   - Download the latest release from the [Releases Page](#).
   
2. **Install in Blender**
   - Open Blender.
   - Go to `Edit` -> `Preferences`.
   - In the Preferences window, go to the `Add-ons` tab.
   - Click `Install...` and select the downloaded `.zip` file containing the plugin.
   - Once installed, enable the plugin by checking the box next to `BlendTagger`.

3. **Access the Plugin**
   - After enabling, you will find the plugin in the sidebar (press `N` to show the sidebar).
   - Look for the "BlendAnnotate" panel where you can start adding annotations to your scene.

---

## **How to Use**

### **Adding Annotations**

1. **Select an Object**: Choose the object or mesh you want to annotate.
2. **Open the Plugin Panel**: Navigate to the `BlendTagger` panel in the sidebar.
3. **Add Tags**: Use the input field to add custom tags to the object (e.g., “chair”, “table”, “car”).
4. **Mark Specific Areas**: For more detailed annotations, you can select specific vertices, edges, or faces of a mesh and assign tags or labels to them.
5. **Export Annotations**: Once your annotations are complete, click the “Export Annotations” button to save the data in JSON, CSV, or other formats suitable for training AI models.

### **Export Formats**

- **JSON**: Stores the annotations in a structured format for easy use in AI model training.
- **CSV**: A tabular format that can be opened in Excel or other data manipulation tools.

---

## **Contributing**

**BlendTagger** is an open-source project, and contributions are welcome! Whether you're reporting a bug, submitting a feature request, or contributing code, we appreciate your help in improving the project.

### **How to Contribute**

1. **Fork the Repository**: Click on the `Fork` button at the top of this repository to create your copy of the project.
2. **Create a Branch**: Create a branch for your feature or bugfix (`git checkout -b feature-branch`).
3. **Make Changes**: Implement your changes or additions.
4. **Push to Your Fork**: Push your changes (`git push origin feature-branch`).
5. **Submit a Pull Request**: Open a pull request to merge your changes into the main repository.

### **Issues**

If you encounter any bugs or have ideas for improvements, please open an issue on the [Issues page](#).

---

## **License**

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.

---

## **Acknowledgments**

- Thanks to the Blender community for making Blender a powerful and open tool.
- Inspired by AI research and efforts to improve 3D object recognition and generation.
- Special thanks to [contributors](#) who help with development.
