import QtQuick 2.0
import QtQuick.Layouts 1.1
// Кнопка для главной страницы
Rectangle {
    id: mybutton
    property string text
    signal clicked
    Layout.fillWidth: true
    width: 200
    height: 100
    radius: 5
    border {
        color: "grey"
        width: 1
    }
    Text {
        id: buttonText
        anchors.centerIn: parent
        text: mybutton.text
    }
    MouseArea {
        anchors.fill: parent
        onClicked: mybutton.clicked()
    }
}
