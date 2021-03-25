import QtQuick 2.15

TableView {
    id: myView

    model: myModel

    delegate: Rectangle {
        implicitWidth: 100
        implicitHeight: 50
        border.width: 1

        Text {
            text: display
            anchors.centerIn: parent
        }

    }

}