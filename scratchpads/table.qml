
TableView {
    id: myView

    topMargin: header.implicitHeight

    Text {
        id: header
        text: "A table header"
    }

    model: myModel
    anchors.fill: parent
    delegate:
        Text {
            text: model.display
        }
}