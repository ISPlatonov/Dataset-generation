import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Dialogs 1.2
import QtQml 2.0
// Попытка сделать главную страницу
/*
1) Изменить кнопку "назад" так, чтобы не открывалось новое окно
2) Добавить скрипт с камерой и соединить его со скриптом про список
*/
import QtQuick.Layouts 1.1

import "."


ApplicationWindow {
    id: mainrect
    //color: Constants.backgroundColor
    width: 480
    height: 640
    visible: true
    title: qsTr("Dataset generator")

    // temp array for 1st step
    //property var firstStepArray: ['qwe', 'wer', 'ert']
    property var name_list: manager.name_list

    Loader {
        id: mainLoader
        visible: true
        source: "mainview.qml"
        anchors.fill: parent
        property int loader_prop_index
        onLoaded: console.log("page is loaded: ", source)
    }

    Connections {
        target: mainLoader.item
        ignoreUnknownSignals: true
        function onGotoStep1() {
            mainLoader.source = "step 1/list.qml"
        }
        function onGotoStep2() {
            mainLoader.source = "step 2/dir.qml"
            console.log("page 2")
        }
        function onGotoStep3() {
            mainLoader.source = "step 3/dir.qml"
            console.log("page 3")
        }
        function onGotoMainView() {
            mainLoader.source = "mainview.qml"
        }
        function onGotoChoosingDir() {
            mainLoader.source = "step 1/dir.qml"
        }
        function onGotoCamera() {
            mainLoader.source = "step 1/camera.qml"
        }
        function onMakeSnapshoot(name) {
            // name snapshot
        }
        function onGotoThreshold() {
            mainLoader.source = "step 2/threshold.qml"
        }
        function onGotoBacks() {
            mainLoader.source = "step 3/backs.qml"
        }
        function onGotoGeneration() {
            mainLoader.source = "step 3/generation.qml"
        }
        /*onLoadArray: {
            item.getArray(mainrect.firstStepArray)
        }*/
    }
}
