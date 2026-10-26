PREFIX ?= /usr/local
DESTDIR ?=
LIBEXECDIR ?= $(PREFIX)/lib/ssh-session-cleanup
DOCDIR ?= $(PREFIX)/share/doc/ssh-session-cleanup
LICENSEDIR ?= $(PREFIX)/share/licenses/ssh-session-cleanup
PKG_CONFIG ?= pkg-config
UNITDIR ?= $(shell $(PKG_CONFIG) --variable=systemdsystemunitdir systemd 2>/dev/null || true)
ifeq ($(strip $(UNITDIR)),)
UNITDIR := $(PREFIX)/lib/systemd/system
endif

.PHONY: all install uninstall check
all:

check:
	python3 -m unittest discover -s tests -v

install:
	install -Dm755 ssh-session-cleanup "$(DESTDIR)$(LIBEXECDIR)/ssh-session-cleanup"
	install -Dm644 README.md "$(DESTDIR)$(DOCDIR)/README.md"
	install -Dm644 LICENSE "$(DESTDIR)$(LICENSEDIR)/LICENSE"
	install -Dm644 ssh-session-cleanup.service "$(DESTDIR)$(UNITDIR)/ssh-session-cleanup.service"
	sed -i -e 's|^ExecStop=.*|ExecStop=$(LIBEXECDIR)/ssh-session-cleanup|' \
	    -e 's|^Documentation=.*|Documentation=file:$(DOCDIR)/README.md|' \
	    "$(DESTDIR)$(UNITDIR)/ssh-session-cleanup.service"

uninstall:
	rm -f "$(DESTDIR)$(LIBEXECDIR)/ssh-session-cleanup" \
	    "$(DESTDIR)$(DOCDIR)/README.md" \
	    "$(DESTDIR)$(LICENSEDIR)/LICENSE" \
	    "$(DESTDIR)$(UNITDIR)/ssh-session-cleanup.service"
