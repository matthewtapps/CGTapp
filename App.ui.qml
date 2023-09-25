

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts

Rectangle {
    id: rectangle
    width: 1000
    height: 600

    color: Constants.backgroundColor

    Pane {
        id: windowPane
        anchors.fill: parent
        padding: 0
        leftPadding: 0
        topPadding: 0

        Frame {
            id: windowFrame
            anchors.fill: parent
            contentWidth: 0

            TextField {
                id: filePathField
                x: 544
                y: 31
                width: 398
                height: 34
                text: "Enter file path to input file"
                overwriteMode: true
                mouseSelectionMode: TextInput.SelectWords
                placeholderText: qsTr("FIle Path")
            }

            MyButton {
                id: filePathButton
                anchors.left: filePathField.right
                anchors.top: filePathField.top
                anchors.topMargin: 0
                anchors.leftMargin: 0
                layer.enabled: false
                enabled: true
                smooth: true
                icon.width: 106
                icon.source: "c:/Users/mattt/Downloads/foldericon.jpg"
            }

            Frame {
                id: outputFrame
                x: 0
                y: 31
                width: 538
                height: 545

                Pane {
                    id: pane
                    anchors.fill: parent
                    anchors.topMargin: -12
                    anchors.leftMargin: -12
                    anchors.bottomMargin: -12
                    anchors.rightMargin: -12
                    padding: 0
                    rightInset: 2
                    bottomInset: 2
                    leftInset: 2
                    topInset: 2
                }

                ScrollView {
                    id: scrollView
                    anchors.fill: parent
                    anchors.topMargin: -12
                    anchors.bottomMargin: -12
                    anchors.leftMargin: -12
                    anchors.rightMargin: -12
                    font.pointSize: 9
                    rightInset: 0
                    bottomInset: 2
                    leftInset: 2
                    topInset: 2
                }
            }

            Text {
                id: titleText
                x: 0
                y: 0
                width: 576
                height: 25
                color: "#ffffff"
                text: qsTr(" Capital Gains Calculator")
                font.pixelSize: 16
                leftPadding: 0
                font.bold: true
                font.capitalization: Font.MixedCase
                styleColor: "#ffffff"
            }

            Button {
                id: button
                y: 487
                text: qsTr("Calculate")
                anchors.left: outputFrame.right
                anchors.right: parent.right
                font.pointSize: 21
                font.bold: true
                anchors.leftMargin: 120
                anchors.rightMargin: 120
            }
        }
    }

    Item {
        id: __materialLibrary__
    }
}
