import * as vscode from "vscode";
import { reviewFileContent } from "./api";

export function activate(context: vscode.ExtensionContext) {
  console.log("RepoSage extension is now active!");

  const disposable = vscode.commands.registerCommand(
    "reposage.reviewCurrentFile",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showInformationMessage(
          "Open a file to review it with RepoSage."
        );
        return;
      }

      const document = editor.document;
      const fileName = document.fileName;
      const fileContent = document.getText();

      vscode.window.showInformationMessage(
        `RepoSage: Reviewing ${fileName}...`
      );

      const result = await reviewFileContent(fileName, fileContent);

      if (result.success) {
        console.log("RepoSage review result:", result.response);
        vscode.window.showInformationMessage(
          "RepoSage review complete! Check the console for details."
        );
      } else {
        vscode.window.showErrorMessage(
          `RepoSage review failed: ${result.error}`
        );
      }
    }
  );

  context.subscriptions.push(disposable);
}

export function deactivate() {}
